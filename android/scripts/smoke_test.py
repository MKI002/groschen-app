#!/usr/bin/env python3
"""Runs the real app on an Android emulator against a Groschen server with invented demo data.

It installs the APK, connects to the server on the computer that runs the emulator, logs in and
opens every page. It fails when the app closes itself, when a page can't load its data, or when
the app logs an unexpected error. A screenshot of each step lands in the given folder.

    python3 smoke_test.py app.apk screenshots/

Needs adb with one emulator, in English, and the demo server on port 8420 with the login below.
"""

import json
import re
import struct
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zlib
from collections import Counter
from pathlib import Path

PACKAGE = "io.github.mki002.groschen"
SERVER = "10.0.2.2:8420"  # how the emulator reaches the computer it runs on
USER, PASSWORD = "alex", "demo-password-123"

# The built-in logos, whose brand colours must show up as discs next to the bookings.
LOGOS = Path(__file__).resolve().parents[2] / "frontend" / "src" / "data" / "logos" / "index.json"

# Texts the app shows when something went wrong (English, see i18n/Strings.kt).
TROUBLE = ("Try again", "Something went wrong", "can't be reached", "No Groschen answers")


def adb(*args: str, check: bool = True) -> str:
    return subprocess.run(["adb", *args], capture_output=True, text=True, check=check, timeout=180).stdout


def press(kind: str, *values: str, tries: int = 3) -> None:
    """Sends a tap, swipe, key or text. Right after the emulator starts, one of these can fail now and then.

    Only [kind] is logged: [values] can be the password typed into the login."""
    for attempt in range(1, tries + 1):
        result = subprocess.run(["adb", "shell", "input", kind, *values], capture_output=True, check=False, timeout=60)
        if result.returncode == 0:
            return
        print(f"input {kind} failed (try {attempt} of {tries}, exit code {result.returncode})")
        time.sleep(2)
    fail(f"The emulator didn't take the input {kind}.")


def fail(why: str) -> None:
    shot("failed")
    print(adb("logcat", "-d", "-t", "120", check=False)[-8000:])
    pid = adb("shell", "pidof", PACKAGE, check=False).strip()
    if pid:
        print("What the app logged:")
        print(adb("logcat", "-d", f"--pid={pid}", check=False)[-8000:])
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
    press("tap", str(x), str(y))
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
        press("swipe", str(x), str(y1 + height * 3 // 4), str(x), str(y1 + height // 4), "400")
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
        press("keyevent", "KEYCODE_BACK")  # with the keyboard up, Back only puts it away
        time.sleep(1)
    fail("The on-screen keyboard didn't go away.")


def type_into(index: int, text: str) -> None:
    fields = [n for n in nodes() if n.get("class") == "android.widget.EditText"]
    if len(fields) <= index:
        fail(f"Expected at least {index + 1} text fields.")
    tap(fields[index])
    press("text", text)
    time.sleep(0.5)
    hide_keyboard()


def no_trouble(page: str) -> None:
    for n in nodes():
        if any(t in label(n) for t in TROUBLE):
            fail(f'{page}: the page shows "{label(n)}".')


def connect(tries: int = 5) -> None:
    """Taps Connect until the login shows. Right after the emulator starts, its network can need a moment."""
    for attempt in range(1, tries + 1):
        tap(lowest(wait_for("Connect")))
        deadline = time.time() + 20
        while time.time() < deadline:
            check_health()
            texts = [label(n) for n in nodes()]
            if texts.count("Log in") >= 2:  # the heading and the button
                return
            if any("can't be reached" in t for t in texts):
                break
            time.sleep(1)
        print(f"Try {attempt}: the app couldn't reach the demo server yet.")
        print(adb("shell", "ping", "-c", "1", "-W", "2", SERVER.split(":")[0], check=False).strip())
        time.sleep(5)
    fail(f"The app couldn't reach the demo server in {tries} tries.")


def shot(name: str) -> None:
    path = Path(sys.argv[2]) / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f, check=False, timeout=60)


def pixels(png: bytes) -> tuple:
    """Width, height, bytes per pixel and the pixels of a screenshot (an 8-bit RGB or RGBA PNG)."""
    width, height, depth, kind, _, _, interlace = struct.unpack(">IIBBBBB", png[16:29])
    if depth != 8 or kind not in (2, 6) or interlace:
        raise ValueError(f"unexpected screenshot format: depth {depth}, colour type {kind}, interlace {interlace}")
    n = 4 if kind == 6 else 3
    data, i = b"", 8
    while i < len(png):
        size, chunk = struct.unpack(">I4s", png[i : i + 8])
        if chunk == b"IDAT":
            data += png[i + 8 : i + 8 + size]
        i += 12 + size
    raw = zlib.decompress(data)
    stride = width * n
    out = bytearray(height * stride)
    prev = bytearray(stride)
    for y in range(height):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1 : (y + 1) * (stride + 1)])
        for x in range(stride):
            a = line[x - n] if x >= n else 0
            b = prev[x]
            c = prev[x - n] if x >= n else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out[y * stride : (y + 1) * stride] = line
        prev = line
    return width, height, n, bytes(out)


def check_logos(page: str) -> None:
    """Brand logos show next to the bookings: round discs in a brand's colour, not only letters."""
    icons = json.loads(LOGOS.read_text(encoding="utf-8"))["icons"]
    colours = {}
    for title, hex6 in icons.values():
        rgb = tuple(int(hex6[i : i + 2], 16) for i in (0, 2, 4))
        if max(rgb) - min(rgb) >= 60:  # grey, black and white brands look like the app itself
            colours.setdefault(rgb, title)
    width, height, n, px = pixels((Path(sys.argv[2]) / f"{page}.png").read_bytes())
    found = Counter()
    for y in range(0, height, 2):
        for x in range(0, width // 3, 2):  # the badges sit on the left
            i = (y * width + x) * n
            rgb = (px[i], px[i + 1], px[i + 2])
            if rgb in colours:
                found[rgb] += 1
    discs = sorted({colours[c] for c, count in found.items() if count >= 30})
    print(f"Logos on {page}:", ", ".join(discs) or "none", f"({sum(found.values())} pixels in brand colours)")
    if not discs:
        fail(f"{page}: no brand logos show, only letters.")


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
    connect()
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
        if tab == "Transactions":
            check_logos(f"{number}-{tab.lower()}")

    tap(lowest(wait_for("Overview")))
    wait_for("FREE TO SPEND UNTIL PAYDAY")
    settle("7-overview-again", 2)

    # The settings, with the update section (a test build doesn't look for updates).
    tap(lowest(wait_for("Settings")))
    time.sleep(2)
    scroll_to("A build of your own doesn't look for updates.")
    settle("8-settings", 2)
    press("keyevent", "KEYCODE_BACK")
    wait_for("FREE TO SPEND UNTIL PAYDAY")

    # Into the background and back, as when switching apps.
    press("keyevent", "KEYCODE_HOME")
    time.sleep(2)
    adb("shell", "am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity")
    settle("9-back-from-background", 3)
    print("The app logged in and opened every page without trouble.")


if __name__ == "__main__":
    main()
