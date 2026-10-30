import { useT, type Key } from "../i18n";
import type { PayoutFrequency, PayoutPolicy } from "../lib/types";

// "Reinvests" or "Pays out quarterly", as a small tag. Nothing when it isn't known.
export function PayoutTag({ policy, frequency, title }: { policy: PayoutPolicy | null | undefined; frequency?: PayoutFrequency | null; title?: string }) {
  const t = useT();
  if (!policy) return null;
  return (
    <span className={`tag ${policy === "accumulating" ? "acc" : "dist"}`} title={title}>
      {payoutText(t, policy, frequency)}
    </span>
  );
}

export function payoutText(t: ReturnType<typeof useT>, policy: PayoutPolicy, frequency?: PayoutFrequency | null) {
  if (policy === "accumulating") return t("pay.acc");
  return frequency ? t(`pay.dist.${frequency}` as Key) : t("pay.dist");
}
