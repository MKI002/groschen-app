import type { ReactElement } from "react";

// Icons from the prototype, drawn inline so nothing is loaded from elsewhere.

const PATHS: Record<string, ReactElement> = {
  "flow": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M7 4v16M7 20l-3-3M7 20l3-3M17 20V4M17 4l-3 3M17 4l3 3"/>
    </>
  ),
  "pie": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M12 3a9 9 0 1 0 9 9h-9z"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>
    </>
  ),
  "list": (
    <>
      <rect x="4" y="3" width="16" height="18" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8"/><path stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M8 8h8M8 12h8M8 16h5"/>
    </>
  ),
  "trend": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M3 17l6-6 4 4 8-8M15 7h6v6"/>
    </>
  ),
  "repeat": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M17 2l3 3-3 3M4 11V9a4 4 0 0 1 4-4h12M7 22l-3-3 3-3M20 13v2a4 4 0 0 1-4 4H4"/>
    </>
  ),
  "bank": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M3 9l9-5 9 5M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>
    </>
  ),
  "car": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M5 16v2M19 16v2M3 12l2-5a2 2 0 0 1 2-1h10a2 2 0 0 1 2 1l2 5v4H3z"/><circle cx="7.5" cy="13" r="1" fill="currentColor"/><circle cx="16.5" cy="13" r="1" fill="currentColor"/>
    </>
  ),
  "etf": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M4 20h16M6 16V11M10 16V7M14 16v-5M18 16V5"/>
    </>
  ),
  "minus": <path stroke="currentColor" strokeWidth="2" strokeLinecap="round" d="M6 12h12" />,
  "plus": (
    <>
      <path stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M12 5v14M5 12h14"/>
    </>
  ),
  "gear": (
    <>
      <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="1.8"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>
    </>
  ),
  "spark": (
    <>
      <path fill="currentColor" d="M12 2l1.8 5.4L19 9l-5.2 1.6L12 16l-1.8-5.4L5 9l5.2-1.6zM19 14l.9 2.6 2.6.9-2.6.9L19 21l-.9-2.6-2.6-.9 2.6-.9z"/>
    </>
  ),
  "warn": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M12 3l10 18H2z"/><path stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M12 10v5M12 18h.01"/>
    </>
  ),
  "lock": (
    <>
      <rect x="4" y="10" width="16" height="11" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8"/><path fill="none" stroke="currentColor" strokeWidth="1.8" d="M8 10V7a4 4 0 0 1 8 0v3"/>
    </>
  ),
  "upload": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 16V4M7 9l5-5 5 5M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>
    </>
  ),
  "home": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M3 11l9-7 9 7M5 10v10h14V10M10 20v-6h4v6" />
  ),
  "tag": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z" />
      <circle cx="8" cy="8" r="1.5" fill="currentColor" />
    </>
  ),
  "plane": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M10 14l-7-3 2-2 7 1 5-5a2 2 0 0 1 3 3l-5 5 1 7-2 2-3-7-3 3v3l-2 1-1-4-4-1 1-2h3z" />
  ),
  "bell": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4zM10 21h4" />
  ),
  "calendar": (
    <>
      <rect x="3.5" y="5" width="17" height="15.5" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8"/><path stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M3.5 10h17M8 3v4M16 3v4"/><path fill="currentColor" d="M7 13.5h2.5V16H7zM11 13.5h2.5V16H11z"/>
    </>
  ),
  "wallet": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" d="M4 7.5A2.5 2.5 0 0 1 6.5 5H18v3M4 7.5V17a2.5 2.5 0 0 0 2.5 2.5H20V8H6.5A2.5 2.5 0 0 1 4 7.5z"/><circle cx="16" cy="14" r="1.3" fill="currentColor"/>
    </>
  ),
  "pencil": <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16zM13.5 6.5l4 4" />,
  "orbit": (
    <>
      <circle cx="12" cy="12" r="2.6" fill="currentColor" />
      <ellipse cx="12" cy="12" rx="9.5" ry="4.2" fill="none" stroke="currentColor" strokeWidth="1.6" transform="rotate(-25 12 12)" />
      <circle cx="19.6" cy="8.4" r="1.6" fill="currentColor" />
    </>
  ),
  "x": <path stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />,
  "check": <path fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M5 12l5 5 9-10" />,
  "refresh": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M20 11a8 8 0 0 0-14.7-4.3M4 5v4h4M4 13a8 8 0 0 0 14.7 4.3M20 19v-4h-4" />
  ),
  "pin": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M9 4h6M10 4v5l-3 4h10l-3-4V4M12 13v7" />
  ),
  "rewind": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4M12 8v4l3 2" />
  ),
  "trash": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6" />
  ),
  "download": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 4v12M7 11l5 5 5-5M4 20h16" />
  ),
  "globe": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z" />
    </>
  ),
  "logout": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 16l-4-4 4-4M6 12h10" />
  ),
  "up": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M5.5 11.5L12 5l6.5 6.5"/>
    </>
  ),
  "down": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 5v14M5.5 12.5L12 19l6.5-6.5"/>
    </>
  ),
  "chevDown": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M6 9l6 6 6-6"/>
    </>
  ),
  "chevRight": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M9 6l6 6-6 6"/>
    </>
  ),
  "search": (
    <>
      <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M20 20l-4.2-4.2"/>
    </>
  ),
  "zoomIn": (
    <>
      <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.8" /><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M20 20l-4.2-4.2M8.2 11h5.6M11 8.2v5.6" />
    </>
  ),
  "zoomOut": (
    <>
      <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="1.8" /><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" d="M20 20l-4.2-4.2M8.2 11h5.6" />
    </>
  ),
  "swap": (
    <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M5 8h13M15 5l3 3-3 3M19 16H6M9 13l-3 3 3 3" />
  ),
  "filter": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><circle cx="9" cy="17" r="2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    </>
  ),
  "sort": (
    <>
      <path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M7 4v16M4 17l3 3 3-3M14 6h7M14 12h5M14 18h3"/>
    </>
  ),
  "coin": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M14.8 9.2a3.6 3.6 0 1 0 0 5.6M8 11h5M8 13.2h5"/>
    </>
  ),
  "vault": (
    <>
      <rect x="3" y="4.5" width="18" height="14.5" rx="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><circle cx="12" cy="11.75" r="3.4" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 6.8v1.4M12 15.3v1.4M7 11.75h1.4M15.6 11.75H17M6.5 19v1.5M17.5 19v1.5"/>
    </>
  ),
  "pause": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M10 9v6M14 9v6"/>
    </>
  ),
  "play": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M10.2 8.8l5 3.2-5 3.2z"/>
    </>
  ),
  "ban": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M5.8 5.8l12.4 12.4"/>
    </>
  ),
  "clock": (
    <>
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/><path fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" d="M12 7v5l3.2 2"/>
    </>
  ),
};

export type IconName = keyof typeof PATHS;

export function Icon({ name, size, className }: { name: string; size?: number; className?: string }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} aria-hidden="true" focusable="false">
      {PATHS[name]}
    </svg>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 40" className={className} aria-hidden="true" focusable="false">
      {/* Colours from the design tokens (--logo-* in styles.css). */}
      <circle cx="20" cy="20" r="18" fill="none" strokeWidth="3" style={{ stroke: "var(--logo-ring)" }} />
      <circle cx="20" cy="20" r="13.5" style={{ fill: "var(--logo-face)" }} />
      <rect x="12.5" y="21" width="4" height="7" rx="1.5" style={{ fill: "var(--logo-bar1)" }} />
      <rect x="18" y="17" width="4" height="11" rx="1.5" style={{ fill: "var(--logo-bar2)" }} />
      <rect x="23.5" y="12.5" width="4" height="15.5" rx="1.5" style={{ fill: "var(--logo-bar3)" }} />
    </svg>
  );
}
