export type Range = { start: string; end: string; label: string };

export type Status = {
  version: string;
  language: string | null;
  has_user: boolean;
  setup_complete: boolean;
  user: { id: number; username: string; name: string } | null;
  passkeys: boolean;
  password_login: boolean;
};

export type JobStep = { label: string; state: "pending" | "running" | "done" | "error" };
export type Job<R = Record<string, unknown>> = {
  id: string;
  kind: string;
  state: "running" | "waiting" | "done" | "error";
  message: string;
  steps: JobStep[];
  result: R | null;
  error: string | null;
};

export type BankAccount = {
  id: number;
  name: string;
  kind: string;
  iban: string | null;
  account_number?: string;
  balance: number | null;
  balance_date?: string | null;
  enabled?: number;
};

export type Connection = {
  id: number;
  bank_code: string;
  bank_name: string;
  short: string;
  status: string;
  last_sync_at: string | null;
  last_error: string | null;
  login_hint: string;
  product_id_set: boolean;
  bank_login_confirmed_at: string;
  login_days_left: number;
  login_due: string;
  accounts: BankAccount[];
};

// A month that cost clearly more than usual (price rises are alerts now).
export type Insight = { key: string; kind: "high_month"; month: string; percent: number; driver: string | null; driver_amount: number | null };

export type Group = {
  name: string;
  color: string;
  amount: number;
  share: number;
  categories: { name: string; amount: number }[];
};

export type Cashflow = {
  range: Range;
  income_total: number;
  spending_total: number;
  saved: number;
  savings_rate: number | null;
  months: number;
  avg_income: number;
  avg_spending: number;
  income: { id: number | null; name: string; amount: number; share: number }[];
  groups: Group[];
  categories: { id: number | null; name: string; group: string; color: string; amount: number; share: number }[];
  monthly: { month: string; income: number; spending: number }[];
  // The chart's steps follow the period: weeks of a single month, months, or years for long histories.
  trend: { unit: "week" | "month" | "year"; points: { key: string; end?: string; from?: number; to?: number; income: number; spending: number }[] };
  transaction_count: number;
  review_count: number;
  insights: Insight[];
  saved_to?: SavedTo;
};

// The Overview timeline: every month, linked by what carried over on the everyday account.
export type TimelineMonth = {
  month: string;
  carry_in: number;
  carry_out: number;
  income: { name: string; id: number | null; amount: number }[];
  spending: { name: string; color: string; amount: number }[];
  placed: { key: SavedGroup; amount: number; focus: SavedDest }[];
  income_total: number;
  spending_total: number;
  stays: number;
};
// account: the everyday account's name when there is one; known: its balance came from the bank;
// ahead: money already on it that counts for next month (salary paid early).
export type Timeline = { months: TimelineMonth[]; account: string | null; known: boolean; ahead: number };

// Where the saved money went (Overview). "stays" is what is left on the account.
export type SavedDest = "plan" | "etf" | "savings" | "other" | "stays";
// The Overview shows only these three: invested, put aside on other accounts, and what stays.
export type SavedGroup = "invested" | "aside" | "stays";
export type SavedItem = {
  id: number;
  date: string;
  amount: number;
  dest: SavedDest;
  auto: SavedDest;
  how: "mirror" | "invest" | "text" | "category" | "user" | "learned";
  from: string | null;
  to: string | null;
  name: string;
  purpose: string;
  learnable: boolean;
};
export type SavedTo = {
  saved: number;
  parts: { key: SavedDest; group: SavedGroup; amount: number; count: number; account: string | null }[];
  items: SavedItem[];
};

export type Tx = {
  id: number;
  date: string;
  amount: number;
  counterparty: string | null;
  purpose: string | null;
  booking_text: string | null;
  category_id: number | null;
  cat_source: string | null;
  confidence: number | null;
  needs_review: number;
  note: string | null;
  account: string;
  category: string | null;
  category_group: string | null;
  category_color: string | null;
  merchant: string;
  counts_for: string | null; // salary paid late in a month: the date it counts for instead
  subscription: "yes" | "no" | null;
  roundup?: boolean; // one of Kleingeld Plus' round-ups (the Transactions list folds them per day)
  detail?: string; // the purpose without bank references, for the second line in lists ("" when it adds nothing)
  refunded?: number | null; // what came back for this payment in all (a refund, someone paying back)
  refund_for?: TxBrief | null; // the payment this money came back for
};

// A booking in a few words, where another one points at it.
export type TxBrief = { id: number; date: string; amount: number; merchant: string };
// Both sides of money that came back: the payment and everything that came back for it.
export type RefundInfo = {
  purchase: TxBrief | null;
  refunds: (TxBrief & { source: "auto" | "user" })[];
  refunded: number;
  left: number | null;
  source: "auto" | "user" | null;
};
// A payment money could have come back for, when linking by hand.
// ``share``: the money is exactly this payment split that many ways (1 = all of it, 2 = half ...).
export type RefundCandidate = TxBrief & { left: number; category: string | null; category_color: string | null; share: number | null };

export type TxPage = { items: Tx[]; total: number; in: number; out: number; review: number; range: Range };

export type Category = { id: number; name: string; group: string; kind: string; color: string; used: number };

export type NetWorth = {
  net_worth: number;
  assets: number;
  liabilities: number;
  change_this_year: number | null;
  accounts: (BankAccount & { side: "asset" | "liability"; source: string; manual: number })[];
  series: { month: string; value: number }[];
};

export type Holding = {
  account_id: number;
  isin: string;
  name: string;
  pieces: number;
  price: number | null;
  price_date: string | null;
  value: number;
  acquisition_price: number | null;
  cost: number | null;
  share: number;
  plan: number | null;
  r1y?: number | null;
  ytd?: number | null;
  vol?: number | null;
  spark?: number[];
  payout?: { policy: PayoutPolicy | null; frequency: PayoutFrequency | null };
};

export type PayoutPolicy = "distributing" | "accumulating";
export type PayoutFrequency = "monthly" | "bimonthly" | "quarterly" | "semiannual" | "annual";

export type Payout = {
  policy: PayoutPolicy | null;
  frequency: PayoutFrequency | null;
  source: "profile" | "bookings" | "name" | null;
  received: { date: string; amount: number }[];
  received_12m: number;
  count_12m: number;
  yield_12m: number | null;
  dividend_yield: number | null;
};

export type FundFacts = {
  policy?: PayoutPolicy;
  frequency?: PayoutFrequency | null;
  ter?: number;
  size?: number;
  size_currency?: string;
  replication?: "physical" | "synthetic";
  replication_detail?: string;
  currency?: string;
  hedged?: boolean;
  domicile?: string;
  inception?: string;
  index?: string;
  dividend_yield?: number;
  fetched_at?: string;
};

export type ForecastInputs = { ret: number; vol: number; years: number; vol_known: boolean; prior: number; hist?: number | null; weight?: number };

export type Investing = {
  rhythm: "monthly" | "quarterly" | "irregular" | "once";
  day: number;
  typical: number;
  per_month: number;
  raise_pa: number;
  // Where per_month comes from: a steady plan, the average of the last months (window), or nothing yet.
  source?: "plan" | "average" | "none";
  steady?: boolean;
  pace?: number;
  window_months?: number;
  window_total?: number;
  window_count?: number;
  this_month?: number;
  recent?: number;
  steps: { from: string; to?: string; amount: number; months: number }[];
  count: number;
  total: number;
  first: string;
  last: string;
  monthly: { month: string; amount: number }[];
  purchases: { date: string; amount: number; price?: number | null }[];
  avg_buy: number | null;
  avg_market: number | null;
  xirr?: number | null;
  // The fund's own price change per year over the same time, as if all had gone in on the first day.
  fund_pa?: number | null;
  estimated?: boolean;
};

export type FundRisk = {
  volatility: number | null;
  max_drawdown: number;
  max_drawdown_from: string;
  max_drawdown_to: string;
  recovered: string | null;
  current_drawdown: number;
  ath: number;
  ath_date: string;
  high_52w: number | null;
  low_52w: number | null;
  cagr: number | null;
  sharpe: number | null;
  months_up: number;
  months: number;
  rolling_up: number | null;
  rolling_best: number | null;
  rolling_worst: number | null;
  rolling_count: number;
  rolling: { month: string; r: number }[]; // every twelve months in a row, by the month they end in
  ma200: number | null;
  years_of_data: number;
  monthly: { month: string; r: number }[];
  drawdown: { month: string; dd: number }[];
};

export type Fund = {
  isin: string;
  name: string;
  position: {
    pieces: number;
    price: number | null;
    price_date: string | null;
    value: number;
    cost: number | null;
    cost_source: "ing" | "payments" | null;
    avg_price: number | null;
    gain: number | null;
    share: number;
    since: string | null;
    cost_pa?: number;
  } | null;
  facts: FundFacts | null;
  payout: Payout;
  prices: { d: string; p: number }[];
  last_price: number | null;
  last_date: string | null;
  first_date: string | null;
  daily: boolean;
  source: { online: boolean; fetched_at?: string | null; error?: string | null; points?: number | null };
  online_enabled: boolean;
  periods: { key: string; r: number; annual: boolean; from: string }[];
  risk: FundRisk | null;
  years: { year: number; r: number; partial: boolean }[];
  investing: Investing | null;
  forecast: ForecastInputs;
};

export type Stats = {
  twr: number | null;
  volatility: number | null;
  max_drawdown: number;
  max_drawdown_month: string;
  sharpe: number | null;
  best: { month: string; r: number };
  worst: { month: string; r: number };
  months_up: number;
  months: number;
  returns: { month: string; r: number }[];
  drawdown: { month: string; dd: number }[];
  risk_free: number;
};

export type Investments = {
  accounts: { id: number; name: string; balance: number }[];
  value: number;
  paid_in: number;
  paid_in_source: string;
  gain: number | null;
  holdings: Holding[];
  series: { month: string; value: number; paid_in: number }[];
  daily?: { date: string; value: number; paid_in: number }[];
  // Each ETF's [value, paid in] on the same days as daily.
  holding_daily?: Record<string, [number, number][]>;
  stats: Stats | null;
  xirr: number | null;
  days_recorded: number;
  price_date: string | null;
  monthly_plan: number;
  allowance: { used: number; limit: number; year: number };
  forecast: ForecastInputs;
  investing: Investing | null;
  online_prices: boolean;
};

export type Interval = "weekly" | "biweekly" | "4-weekly" | "monthly" | "bimonthly" | "quarterly" | "half-yearly" | "yearly";

export type Subscription = {
  key: string;
  name: string;
  merchant: string;
  category: string | null;
  group: string | null;
  amount: number;
  previous_amount: number;
  price_change: number;
  price_change_date: string | null;
  changes: { date: string; from: number; to: number }[];
  interval: Interval;
  rhythm_known: boolean;
  monthly_cost: number;
  yearly_cost: number;
  count: number;
  first_date: string;
  since: string;
  last_date: string;
  next_date: string;
  day: number;
  varies: boolean;
  confirmed: boolean;
  // new: recently started; resumed: back after a pause; ended: stopped coming (cancelled).
  status: "active" | "new" | "resumed" | "ended";
  new_since: string | null;
  ended_on: string | null;
  pause_days: number | null;
  runs: { from: string; to: string }[];
  history: { date: string; amount: number }[];
  auto?: "rhythm" | "category" | "contract";
  reason?: "twice" | "varies";
};

export type HiddenSubscription = { key: string; name: string; amount: number; last_date: string };

// Something that changed with a recurring payment, found by Groschen itself.
export type SubEvent = {
  key: string;
  kind: "price_up" | "price_down" | "new" | "ended" | "resumed";
  date: string;
  sub: string;
  name: string;
  merchant: string;
  interval: Interval;
  amount: number;
  monthly_cost: number;
  from?: number;
  to?: number;
  per_year?: number;
  last_date?: string;
  pause_days?: number;
  since?: string;
};

export type Subscriptions = {
  items: Subscription[];
  monthly: number;
  yearly: number;
  price_changes: Subscription[];
  suggestions: Subscription[];
  hidden: HiddenSubscription[];
  ended: Subscription[];
  events: SubEvent[];
};

// A savings plan Groschen found: ETF plans, Kleingeld Plus, standing orders to savings.
export type Plan = {
  key: string;
  kind: "etf" | "roundup" | "savings";
  name: string;
  isin: string | null;
  invested: boolean;
  amount: number;
  day: number;
  since: string;
  streak: number;
  total: number;
  total_all: number;
  first_date: string;
  last_date: string;
  next_date: string | null;
  active: boolean;
  state: "running" | "paused" | "ended";
  changes: { month: string; from: number; to: number }[];
  months: { month: string; amount: number }[];
};

// items: running and paused plans; ended: plans that missed about three payments.
export type Plans = { items: Plan[]; ended: Plan[]; running: number; monthly: number; invested_monthly: number; saved_monthly: number };

export type Badges = { review: number; price_changes: number; transactions: number; reminder_days: number; alerts: number };

export type PlannedCharge = {
  date: string;
  name: string;
  payee: string;
  amount: number;
  kind: "fixed" | "transfer";
  category: string | null;
  interval: string;
};

export type Available =
  | { has_account: false }
  | {
      has_account: true;
      balance: number;
      balance_date: string;
      balance_age_days: number;
      payday: { date: string; late: boolean; usual_day: number; name: string; amount: number; last: string } | null;
      since: string;
      until: string;
      days: number;
      upcoming: PlannedCharge[];
      fixed_total: number;
      buffer: number;
      available: number;
      per_day: number;
    };

export type CalendarEntry = {
  date: string;
  name: string;
  amount: number;
  kind: "fixed" | "transfer" | "income";
  status: "paid" | "expected";
  interval: string;
  category: string | null;
  tx_id: number | null;
};

export type CalendarMonth = {
  month: string;
  today: string;
  entries: CalendarEntry[];
  paid: number;
  expected: number;
  total: number;
  income: number;
};

export type Alert =
  | { key: string; kind: "duplicate"; date: string; name: string; amount: number; first_date: string; account: string; tx_ids: number[] }
  | (SubEvent & { kind: "price_up" | "price_down" })
  | (Omit<SubEvent, "kind"> & { kind: "sub_new" | "sub_ended" | "sub_resumed" })
  | {
      key: string;
      kind: "unusual";
      date: string;
      name: string;
      amount: number;
      category: string | null;
      tx_id: number;
      basis: "merchant" | "category" | "new";
      usual: number | null;
    };

export type SettingsValues = {
  setup_complete: boolean;
  session_days: number;
  idle_minutes: number;
  login_max_failures: number;
  login_lock_minutes: number;
  password_login: boolean;
  categorizer: "model" | "rules";
  language: "de" | "en" | null;
  sync_schedule: "daily" | "twice" | "6h";
  reminder_days: number;
  unusual_alerts: boolean;
  alert_duplicates: boolean;
  alert_price_up: boolean;
  alert_subscriptions: boolean;
  alert_unusual: boolean;
  alert_large: number;
  safe_buffer: number;
  payday_shift: boolean;
  review_uncertain: boolean;
  risk_free_rate: number;
  tax_allowance: number;
  online_prices: boolean;
  backup_plan: BackupPlan;
  backup_nightly: boolean;
  backup_schedule: BackupSchedule;
  backup_hour: number;
  backup_mode: BackupMode;
  backup_keep: number;
  backup_days: number;
  backup_smart_days: number;
  backup_smart_weeks: number;
  backup_smart_months: number;
  backup_smart_years: number;
  backup_max: number;
  holder_names: string[];
};

export type BackupSchedule = "hourly" | "6h" | "twice" | "daily" | "weekly" | "off";
export type BackupMode = "last" | "days" | "smart";
export type BackupPlan = "smart" | "custom";
export type Backup = {
  name: string;
  size: number;
  created_at: string;
  kind: "auto" | "manual" | "safety";
  pinned: boolean;
  transactions?: number;
  accounts?: number;
  latest?: string | null;
};

export type SettingsInfo = {
  values: SettingsValues;
  version: string;
  model: { kind: string; label: string; loaded: boolean };
  learning: { corrections: number; memory: number; rules: number; recent: number; recent_auto: number };
  network: {
    days: number;
    count: number;
    hosts: string[];
    blocked: string[];
    entries: { ts: string; host: string; purpose: string | null; allowed: number }[];
    allowed_hosts: string[];
  };
  backups: Backup[];
  next_runs: Record<string, string>;
  market: { enabled: boolean; host: string; last: string | null; funds: { isin: string; fetched_at: string | null; first_date: string | null; last_date: string | null; points: number | null; error: string | null }[] };
};

// name: the merchant as lists show it; key: what Groschen matches bookings by.
export type Learned = { key: string; name: string; category_id: number; hits: number; updated_at: string; category: string; category_group: string; color: string };
export type Rule = { id: number; field: string; op: string; value: string; category_id: number; category: string; color: string };
export type UserGroup = { id: number; name: string; icon: string; category_ids: number[] };

export type Drilldown = {
  scope: { kind: "group" | "category" | "merchant" | "custom"; name: string; group: string; color: string; direction: "spending" | "income"; category_id: number | null; custom_id?: number | null };
  range: Range;
  categories: { id: number | null; name: string; color: string; amount: number; count: number }[];
  summary: {
    total: number;
    count: number;
    average: number;
    median: number;
    per_month: number;
    months: number;
    largest: { id: number; date: string; merchant: string; value: number } | null;
    review: number;
    previous: { start: string; end: string; total: number; count: number } | null;
  };
  monthly: { month: string; amount: number; count: number }[];
  weekday: { day: number; amount: number; count: number }[];
  merchants: { name: string; amount: number; count: number; share: number }[];
  merchant_count: number;
  all_time: { total: number; count: number; first: string; last: string; monthly: { month: string; amount: number }[] } | null;
  items: Tx[];
  total: number;
};

export type Payday = {
  key: string;
  name: string;
  usual_day: number;
  amount: number;
  count: number;
  last_date: string;
  auto: "next" | "early" | "same";
  mode: "auto" | "next" | "same";
  moved: number;
};

export type Paydays = { enabled: boolean; sources: Payday[] };

// A payment Groschen counts as money put into (or taken out of) investments.
export type InvestPayment = {
  id: number;
  date: string;
  amount: number;
  isin: string | null;
  how: "category" | "detected";
  counted: boolean;
  name: string;
  purpose: string;
  category: string | null;
};

export type Passkey = { id: number; name: string; rp_id: string; created_at: string; last_used_at: string | null };
export type LoginSession = {
  id: number;
  current: boolean;
  created_at: string;
  last_seen: string;
  ip: string | null;
  agent: string | null;
  method: "password" | "passkey";
};
export type LoginEvent = { at: string; username: string | null; method: "password" | "passkey"; ok: number; ip: string | null; agent: string | null };
