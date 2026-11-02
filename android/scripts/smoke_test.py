#!/usr/bin/env python3
"""Runs the real app on an Android emulator against a Groschen server with invented demo data.

It installs the APK, connects to the server on the computer that runs the emulator, logs in and
opens every page. It fails when the app closes itself, when a page can't load its data, or when
the app logs an unexpected error. A screenshot of each step lands in the given folder.

    python3 smoke_test.py app.apk screenshots/

Needs adb with one emulator, in English, and the demo server on port 8420 with the login below.
"""

import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE = "io.github.mki002.groschen"
SERVER = "10.0.2.2:8420"  # how the emulator reaches the computer it runs on
USER, PASSWORD = "alex", "demo-password-123"

# Texts the app shows when something went wrong (English, see i18n/Strings.kt).
TROUBLE = ("Try again", "Something went wrong", "can't be reached", "No Groschen answers")


def adb(*args: str, check: bool = True) -> str:
    return subprocess.run(["adb", *args], capture_output=True, text=True, check=check, timeout=180).stdout


def fail(why: str) -> None:
    shot("failed")
    print(adb("logcat", "-d", "-t", "300", check=False)[-12000:])
    print(adb("logcat", "-d", "-b", "crash", check=False)[-6000:])
    print("On the screen:", " | ".join(t for t in (label(n) for n in nodes()) if t))
    print("On-screen keyboard up:", keyboard_shown())
    print(f"::error::{why}")
    sys.exit(1)


def check_health() -> None:
    crash = adb("logcat", "-d", "-b", "crash", check=False)
    if PACKAGE in crash:
        print(crash[-6000:])
        fail("The app crashed.")
    if not adb("shell", "pidof", PACKAGE, check=False).strip():
        fail("The app is no longer running.")
    mistakes = adb("logcat", "-d", "-s", "Groschen:E", check=False)
    if "Unexpected error" in mistakes:
        print(mistakes[-6000:])
        fail("The app logged an unexpected error.")


def nodes() -> list:
    for _ in range(5):
        out = subprocess.run(
            ["adb", "exec-out", "uiautomator", "dump", "/dev/tty"], capture_output=True, text=True, check=False, timeout=60
        ).stdout
        start, end = out.find("<?xml"), out.rfind("</hierarchy>")
        if start >= 0 and end >= 0:
            return list(ET.fromstring(out[start : end + len("</hierarchy>")]).iter("node"))
        time.sleep(1)
    return []


def label(node) -> str:
    return node.get("text") or node.get("content-desc") or ""


def bounds(node) -> tuple:
    return tuple(map(int, re.findall(r"\d+", node.get("bounds"))))


def center(node) -> tuple:
    x1, y1, x2, y2 = bounds(node)
    return (x1 + x2) // 2, (y1 + y2) // 2


def wait_for(text: str, timeout: int = 60, at_least: int = 1) -> list:
    deadline = time.time() + timeout
    while time.time() < deadline:
        check_health()
        found = [n for n in nodes() if label(n) == text]
        if len(found) >= at_least:
            return found
        time.sleep(1)
    fail(f'"{text}" did not show up within {timeout} seconds.')


def tap(node) -> None:
    x, y = center(node)
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(0.8)


def scroll_to(text: str, tries: int = 8) -> None:
    """Swipes up until [text] is on the screen (a long sheet shows only part of itself)."""
    for _ in range(tries):
        found = nodes()
        if any(label(n) == text for n in found):
            return
        # Swipe inside the biggest scrolling area, so the swipe can't land on something else.
        areas = [bounds(n) for n in found if n.get("scrollable") == "true"] or [bounds(n) for n in found[:1]]
        x1, y1, x2, y2 = max(areas, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if areas else (0, 0, 320, 640)
        x, height = (x1 + x2) // 2, y2 - y1
        adb("shell", "input", "swipe", str(x), str(y1 + height * 3 // 4), str(x), str(y1 + height // 4), "400")
        time.sleep(1)
        check_health()
    fail(f'"{text}" did not show up after scrolling.')


def lowest(found: list):
    """The same text twice (a title and a button): the one further down is the button."""
    return max(found, key=lambda n: center(n)[1])


def keyboard_shown() -> bool:
    return "mInputShown=true" in adb("shell", "dumpsys", "input_method", check=False)


def hide_keyboard() -> None:
    """The on-screen keyboard covers the lower half of the small test screen, and with it the buttons."""
    for _ in range(3):
        if not keyboard_shown():
            return
        adb("shell", "input", "keyevent", "KEYCODE_BACK")  # with the keyboard up, Back only puts it away
        time.sleep(1)
    fail("The on-screen keyboard didn't go away.")


def type_into(index: int, text: str) -> None:
    fields = [n for n in nodes() if n.get("class") == "android.widget.EditText"]
    if len(fields) <= index:
        fail(f"Expected at least {index + 1} text fields.")
    tap(fields[index])
    adb("shell", "input", "text", text)
    time.sleep(0.5)
    hide_keyboard()


def no_trouble(page: str) -> None:
    for n in nodes():
        if any(t in label(n) for t in TROUBLE):
            fail(f'{page}: the page shows "{label(n)}".')


def shot(name: str) -> None:
    path = Path(sys.argv[2]) / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f, check=False, timeout=60)


def settle(page: str, seconds: float = 5) -> None:
    time.sleep(seconds)
    check_health()
    no_trouble(page)
    shot(page)
    print(f"ok: {page}:", " | ".join(t for t in (label(n) for n in nodes()) if t)[:400])


def main() -> None:
    apk = sys.argv[1]
    adb("install", "-r", apk)
    adb("logcat", "-c")
    adb("shell", "am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity")

    wait_for("Connect to your Groschen")
    shot("1-connect")
    type_into(0, SERVER)
    tap(lowest(wait_for("Connect")))

    wait_for("Log in")
    shot("2-login")
    type_into(0, USER)
    type_into(1, PASSWORD)
    tap(lowest(wait_for("Log in", at_least=2)))  # the heading and the button

    # Small headings are shown in capitals.
    wait_for("FREE TO SPEND UNTIL PAYDAY")
    settle("3-overview")

    for number, tab in enumerate(("Transactions", "Spending", "Wealth"), start=4):
        tap(lowest(wait_for(tab)))
        settle(f"{number}-{tab.lower()}")

    tap(lowest(wait_for("Overview")))
    wait_for("FREE TO SPEND UNTIL PAYDAY")
    settle("7-overview-again", 2)

    # The settings, with the update section (a test build doesn't look for updates).
    tap(lowest(wait_for("Settings")))
    time.sleep(2)
    scroll_to("A build of your own doesn't look for updates.")
    settle("8-settings", 2)
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    wait_for("FREE TO SPEND UNTIL PAYDAY")

    # Into the background and back, as when switching apps.
    adb("shell", "input", "keyevent", "KEYCODE_HOME")
    time.sleep(2)
    adb("shell", "am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity")
    settle("9-back-from-background", 3)
    print("The app logged in and opened every page without trouble.")


if __name__ == "__main__":
    main()
