"""Talking to the bank over FinTS (HBCI), read-only.

Only reading operations are used: account list, balances, transactions and
depot holdings. Groschen never sends payment orders.

The adapter returns plain dictionaries so the rest of the app (and the tests)
never touch python-fints objects directly.
"""

import datetime as dt
import logging
import re
import time
from decimal import Decimal

from ..jobs import UserFacingError
from . import banks

log = logging.getLogger("groschen.fints")

DECOUPLED_TIMEOUT = 180  # seconds to wait for an approval in the banking app
HISTORY_DAYS = 90  # what banks hand out without a TAN (PSD2)

# Words in the names banks give their app-based approval, for banks whose parameters don't say so.
_APP_WORDS = re.compile(r"push|securego|bestsign|secureplus|decoupled|entkoppelt|\bapp\b", re.I)


def bank_info(bank_code: str, server: str | None = None) -> dict:
    """Name, short name, FinTS address and app of the bank behind a Bankleitzahl."""
    info = banks.resolve(None, bank_code, server)
    if not info["server"]:
        raise UserFacingError(
            "Groschen doesn't know the FinTS address of this bank yet. Enter it under Advanced: "
            "your bank lists it on its website (search for FinTS or HBCI PIN/TAN)."
        )
    return {**info, "history_days": HISTORY_DAYS}


def account_kind(fints_type: int | None, product_name: str | None) -> str:
    """Map the FinTS account type (1-99) to Groschen's account kinds."""
    name = (product_name or "").lower()
    if fints_type is None:
        if "depot" in name:
            return "depot"
        if "extra" in name or "tagesgeld" in name or "spar" in name:
            return "savings"
        return "checking"
    if 1 <= fints_type <= 9:
        return "checking"
    if 10 <= fints_type <= 29:
        return "savings"
    if 30 <= fints_type <= 39 or 60 <= fints_type <= 69:
        return "depot"
    if 40 <= fints_type <= 49:
        return "loan"
    if 50 <= fints_type <= 59:
        return "credit_card"
    return "checking"


def _to_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (dt.date, dt.datetime)):
        return dt.date(value.year, value.month, value.day).isoformat()
    try:
        return dt.date(int(value.year), int(value.month), int(value.day)).isoformat()
    except (AttributeError, TypeError, ValueError):
        return str(value)[:10]


def _to_float(value) -> float:
    if value is None:
        return 0.0
    if hasattr(value, "amount"):
        value = value.amount
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def map_transaction(data: dict) -> dict:
    amount = data.get("amount")
    currency = getattr(amount, "currency", None) or data.get("currency") or "EUR"
    booking = data.get("entry_date") or data.get("date")
    return {
        "date": _to_date(booking),
        "value_date": _to_date(data.get("date")),
        "amount": round(_to_float(amount), 2),
        "currency": currency,
        "counterparty": (data.get("applicant_name") or "").strip() or None,
        "counterparty_iban": (data.get("applicant_iban") or "").strip() or None,
        "purpose": (data.get("purpose") or "").strip() or None,
        "booking_text": (data.get("posting_text") or "").strip() or None,
    }


def map_holding(h) -> dict:
    return {
        "isin": h.ISIN,
        "name": (h.name or "").strip(),
        "pieces": float(h.pieces or 0),
        "price": float(h.market_value) if h.market_value is not None else None,
        "price_date": _to_date(h.valuation_date),
        "value": float(h.total_value) if h.total_value is not None else float(h.pieces or 0) * float(h.market_value or 0),
        "acquisition_price": float(h.acquisitionprice) if h.acquisitionprice is not None else None,
    }


def _explain(exc: Exception, bank: str = "The bank") -> UserFacingError:
    text = str(exc)
    lower = text.lower()
    name = type(exc).__name__
    if name == "FinTSClientPINError" or (
        "pin" in lower and ("falsch" in lower or "wrong" in lower or "ungültig" in lower or "gesperrt" in lower)
    ):
        return UserFacingError(f"{bank} didn't accept the login or PIN. Check both and try again.")
    if name == "FinTSClientTemporaryAuthError":
        return UserFacingError(f"{bank} has locked the online access for now. Unlock it in your online banking first.")
    if "9010" in text or "9050" in text or "9800" in text or "9942" in text:
        return UserFacingError(
            f"{bank} refused the request. Log in to your online banking once, check that FinTS (HBCI) "
            f"access is turned on there, and try again. The bank said: {text}"
        )
    if "Blocked by Groschen" in text:
        return UserFacingError(text)
    if "Max retries" in text or "Connection" in text or "timed out" in lower or "Name or service" in text:
        return UserFacingError(
            f"Groschen couldn't reach {bank}. Check that the server has internet access and the FinTS address is right."
        )
    return UserFacingError(f"{bank} returned an error: {text}")


def _app_score(parameter) -> int:
    """How sure it is that this TAN method approves in an app, without a TAN to type (0 to 2)."""
    if getattr(parameter, "decoupled_max_poll_number", None) is not None:
        return 2
    return int(bool(_APP_WORDS.search(str(getattr(parameter, "name", "") or ""))))


def challenge_view(response) -> dict:
    """What the web page shows for a TAN request: the bank's text and, for photoTAN, the picture."""
    import base64

    view = {"text": getattr(response, "challenge", None) or "", "image": None}
    matrix = getattr(response, "challenge_matrix", None)
    if matrix and matrix[0] in ("image/png", "image/jpeg", "image/gif"):
        view["image"] = f"data:{matrix[0]};base64,{base64.b64encode(matrix[1]).decode()}"
    return view


class FinTSSession:
    """One conversation with the bank. Use as a context manager.

    on_wait(message) says the bank waits for an approval in its app. on_tan(challenge)
    asks the person at the web page for a TAN and returns it, or None when nobody can answer
    (a sync running at night).
    """

    def __init__(
        self,
        bank_code: str,
        login: str,
        pin: str,
        product_id: str,
        state: bytes | None = None,
        on_wait=None,
        server: str | None = None,
        on_tan=None,
    ):
        from fints.client import FinTS3PinTanClient

        self.info = bank_info(bank_code, server)
        self.bank_code = bank_code
        self.on_wait = on_wait or (lambda msg: None)
        self.on_tan = on_tan
        # Set once the user approved a request in the banking app or typed a TAN: that is the
        # login the bank asks for every 90 days, so the countdown can start again by itself.
        self.approved = False
        if not product_id:
            raise UserFacingError("A FinTS product ID is needed. You get one free from the Deutsche Kreditwirtschaft.")
        server = self.info["server"]
        try:
            self.client = FinTS3PinTanClient(bank_code, login, pin, server, product_id=product_id, from_data=state)
        except Exception:
            # Stored state from an older version can be unreadable: start fresh.
            self.client = FinTS3PinTanClient(bank_code, login, pin, server, product_id=product_id)

    @property
    def bank(self) -> str:
        return self.info["label"]

    def __enter__(self):
        try:
            if not self.client.get_current_tan_mechanism():
                self.client.fetch_tan_mechanisms()
                if self.info["id"] != "ing":  # ING logs in with the PIN alone
                    self._prefer_app()
            self.client.__enter__()
            if self.client.init_tan_response:
                self._resolve(self.client.init_tan_response)
        except UserFacingError:
            raise
        except Exception as exc:
            raise _explain(exc, self.bank) from exc
        return self

    def _prefer_app(self) -> None:
        """Choose approval in the banking app over TANs to type, and the device it runs on.

        python-fints takes the first method the bank lists, which is often chipTAN. An app
        approval also works for the daily sync, as long as someone has the phone.
        """
        try:
            methods = self.client.get_tan_mechanisms()
        except Exception as err:
            log.debug("Couldn't list the TAN methods: %s", err)
            return
        usable = {k: p for k, p in methods.items() if k != "999" and str(getattr(p, "tan_process", "2")) == "2"}
        scored = sorted(((_app_score(p), k) for k, p in usable.items()), key=lambda x: -x[0])
        app = scored[0][1] if scored and scored[0][0] else None
        if app and app != self.client.get_current_tan_mechanism():
            self.client.set_tan_mechanism(app)
        chosen = usable.get(self.client.get_current_tan_mechanism())
        if chosen is None or str(getattr(chosen, "description_required", "")) != "2":
            return
        try:
            _, media = self.client.get_tan_media()
        except Exception as err:
            log.debug("Couldn't list the TAN devices: %s", err)
            return
        active = [m for m in media or [] if getattr(m, "tan_medium_name", None)]
        if active:
            self.client.set_tan_medium(active[0])

    def __exit__(self, *exc):
        try:
            self.client.__exit__(*exc)
        except Exception as err:  # closing the dialog can fail after an error; nothing is lost
            log.debug("Closing the FinTS dialog failed: %s", err)

    def state(self) -> bytes:
        return self.client.deconstruct(including_private=True)

    def _resolve(self, response):
        from fints.client import NeedTANResponse

        started = time.monotonic()
        while isinstance(response, NeedTANResponse):
            if not response.decoupled:
                tan = self.on_tan(challenge_view(response)) if self.on_tan else None
                if not tan:
                    raise UserFacingError(
                        f"{self.bank} asked for a TAN. Press Sync now in Groschen while you have your TAN device, "
                        "and type the TAN when Groschen asks."
                    )
                response = self.client.send_tan(response, tan.strip())
                if not isinstance(response, NeedTANResponse):
                    self.approved = True
                continue
            if time.monotonic() - started > DECOUPLED_TIMEOUT:
                raise UserFacingError("The approval in your banking app timed out. Try again when you have your phone.")
            self.on_wait("Please approve the request in your banking app.")
            time.sleep(3)
            response = self.client.send_tan(response, "")
            if not isinstance(response, NeedTANResponse):
                self.approved = True
        return response

    def _call(self, fn, *args):
        try:
            return self._resolve(fn(*args))
        except UserFacingError:
            raise
        except Exception as exc:
            raise _explain(exc, self.bank) from exc

    def accounts(self) -> list[dict]:
        """All accounts, including the depot (which has no IBAN and is missing from the SEPA list)."""
        sepa = self._call(self.client.get_sepa_accounts) or []
        info = self.client.get_information()
        upd = info.get("accounts", [])
        out = []
        seen_numbers = set()
        for acc in sepa:
            meta = next((u for u in upd if u.get("iban") == acc.iban or u.get("account_number") == acc.accountnumber), {})
            out.append(
                {
                    "sepa": acc,
                    "kind": account_kind(meta.get("type"), meta.get("product_name")),
                    "name": meta.get("product_name") or "Account",
                    "iban": acc.iban,
                    "account_number": acc.accountnumber,
                    "subaccount": acc.subaccount,
                    "bic": acc.bic,
                    "blz": acc.blz,
                    "currency": meta.get("currency") or "EUR",
                    "owners": [n.strip() for n in (meta.get("owner_name") or []) if n and n.strip()],
                }
            )
            seen_numbers.add(acc.accountnumber)
        from fints.models import SEPAAccount

        # A depot has no IBAN or BIC of its own: the bank's BIC comes from its other accounts.
        bic = self.info.get("bic") or next((a.bic for a in sepa if a.bic), None)
        for u in upd:
            number = u.get("account_number")
            if not number or number in seen_numbers:
                continue
            kind = account_kind(u.get("type"), u.get("product_name"))
            if kind != "depot":
                continue
            sepa_like = SEPAAccount(
                iban=None,
                bic=bic,
                accountnumber=number,
                subaccount=u.get("subaccount_number"),
                blz=self.bank_code,
            )
            out.append(
                {
                    "sepa": sepa_like,
                    "kind": "depot",
                    "name": u.get("product_name") or "Depot",
                    "iban": None,
                    "account_number": number,
                    "subaccount": u.get("subaccount_number"),
                    "bic": bic,
                    "blz": self.bank_code,
                    "currency": u.get("currency") or "EUR",
                }
            )
            seen_numbers.add(number)
        return out

    def balance(self, account: dict) -> tuple[float, str] | None:
        bal = self._call(self.client.get_balance, account["sepa"])
        if bal is None:
            return None
        return round(_to_float(bal.amount), 2), _to_date(bal.date) or dt.date.today().isoformat()

    def transactions(self, account: dict, since: dt.date) -> list[dict]:
        raw = self._call(self.client.get_transactions, account["sepa"], since, dt.date.today()) or []
        out = []
        for t in raw:
            data = getattr(t, "data", t)
            mapped = map_transaction(data)
            if mapped["date"]:
                out.append(mapped)
        return out

    def holdings(self, account: dict) -> list[dict]:
        raw = self._call(self.client.get_holdings, account["sepa"]) or []
        return [map_holding(h) for h in raw if getattr(h, "ISIN", None)]


def public_account(acc: dict) -> dict:
    return {k: v for k, v in acc.items() if k != "sepa"}
