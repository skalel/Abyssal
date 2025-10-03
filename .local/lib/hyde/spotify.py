#!/usr/bin/python3

import subprocess
import time
import sys
import json
import html

ICON = ""
MAX_TOTAL = 30
MAX_CHAR = 12
SCROLL_DELAY = 0.2


def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def escape_pango(text):
    return html.escape(text, quote=False)


def get_metadata():
    """Lê metadados completos."""
    artist = run(["playerctl", "metadata", "--format", "{{artist}}"])
    title = run(["playerctl", "metadata", "--format", "{{title}}"])
    status = run(["playerctl", "status"]).lower()
    length = run(["playerctl", "metadata", "--format", "{{mpris:length}}"])
    position = run(["playerctl", "position"])
    if status not in ["playing", "paused"]:
        return None
    try:
        total_sec = int(length) // 1000000
    except ValueError:
        total_sec = 0
    try:
        current_sec = int(float(position))
    except ValueError:
        current_sec = 0
    return {
        "artist": artist,
        "title": title,
        "status": status,
        "length": total_sec,
        "position": current_sec
    }


def marquee(text, pos, max_len):
    """Efeito marquee individual."""
    if len(text) <= max_len:
        return text.ljust(max_len)
    text = text + "   "
    idx = pos % len(text)
    return (text + text)[idx:idx + max_len]


def format_time(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"


def build_progress_bar(current, total, width=20):
    if total == 0:
        return ("─" * width, "")
    filled = int(width * current / total)
    empty = width - filled
    return ("─" * empty, "─" * filled)


def build_tooltip(meta):
    """Gera tooltip estilo Hyde Shell."""
    artist = escape_pango(meta["artist"])
    title = escape_pango(meta["title"])
    current = format_time(meta["position"])
    total = format_time(meta["length"])
    filled, empty = build_progress_bar(meta["position"], meta["length"], 10)

    tooltip = (
        f"<span foreground=\"#FFFFFF\"><b>{title}</b></span>\n"
        f"<span foreground=\"#F0E7AA\"><i>{artist}</i></span>\n"
        f"<span foreground=\"#FFFFFF\">{current}</span> "
        f"<span foreground=\"#CCC5C0\">{empty}</span>"
        f"<span foreground=\"#4B5F7D\">{filled}</span> "
        f"<span foreground=\"#FFFFFF\">{total}</span>\n"
        f"<span size='x-small' foreground='#AAAAAA'>🎧 spotify\n🖱 click → play/pause\n🖱 scroll → volume +/-\n🖱 right-click → options</span>"
    )
    return tooltip


def print_json(text, tooltip, player_class):
    sys.stdout.write(json.dumps({
        "text": text,
        "tooltip": tooltip,
        "class": player_class
    }) + "\n")
    sys.stdout.flush()


def main():
    scroll_artist = 0
    scroll_title = 0
    last_meta = None

    while True:
        meta = get_metadata()
        if not meta:
            print_json("", "", "stopped")
            time.sleep(1)
            continue
        
        status_icon = "󰏤" if meta["status"] == "paused" else ""

        key = (meta["artist"], meta["title"])
        if key != last_meta:
            scroll_artist = 0
            scroll_title = 0
            last_meta = key

        artist = escape_pango(meta["artist"])
        title = escape_pango(meta["title"])

        artist_over = len(artist) > MAX_CHAR
        title_over = len(title) > MAX_CHAR

        if artist_over:
            artist_disp = marquee(artist, scroll_artist, MAX_CHAR)
            scroll_artist += 1
        else:
            artist_disp = artist

        if title_over:
            title_disp = marquee(title, scroll_title, MAX_CHAR)
            scroll_title += 1
        else:
            title_disp = title

        display_text = f"<i>{artist_disp}</i> • <b>{title_disp}</b>"
        text = f"{ICON} {status_icon} {display_text}"

        tooltip = build_tooltip(meta)
        print_json(text, tooltip, meta["status"])

        time.sleep(SCROLL_DELAY)


if __name__ == "__main__":
    main()
