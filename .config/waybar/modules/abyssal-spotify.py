#!/usr/bin/python3

import subprocess
import time
import sys
import json
import html
import os
import shutil

ICON = ""
MAX_CHAR = 12
SCROLL_DELAY = 0.2

def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

def escape_pango(text):
    return html.escape(text, quote=False)

def is_spotify_running():
    try:
        out = subprocess.check_output(["pgrep", "-x", "spotify"], text=True).strip()
        return bool(out)
    except subprocess.CalledProcessError:
        return False

def _cmd_exists(cmd):
    return shutil.which(cmd) is not None

def launch_spotify():
    """
    Tenta iniciar o Spotify de forma independente do processo pai.
    1) systemd-run --user --scope (melhor quando disponível)
    2) enfileira via at (se disponível)
    """
    if _cmd_exists("systemd-run"):
        gtk = shutil.which("gtk-launch") or "gtk-launch"
        try:
            subprocess.Popen(
                ["systemd-run", "--user", "--scope", "--unit=spotify-launch", gtk, "spotify"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return
        except Exception:
            pass

    # 2) fallback: enfileirar via 'at' (se atd estiver instalado)
    if _cmd_exists("at"):
        try:
            cmd = "gtk-launch spotify"
            subprocess.Popen(["bash", "-lc", f'echo "{cmd}" | at now'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass

    try:
        subprocess.Popen(["setsid", "gtk-launch", "spotify"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         preexec_fn=os.setpgrp)
    except Exception:
        print("launch_spotify: falha ao iniciar spotify por métodos conhecidos", file=sys.stderr)

def toggle_play_pause():
    subprocess.Popen(["playerctl", "play-pause", "--player=spotify"])

def get_metadata():
    artist = run(["playerctl", "metadata", "--player=spotify", "--format", "{{artist}}"])
    title = run(["playerctl", "metadata", "--player=spotify", "--format", "{{title}}"])
    status = run(["playerctl", "status", "--player=spotify"]).lower()
    length = run(["playerctl", "metadata", "--player=spotify", "--format", "{{mpris:length}}"])
    position = run(["playerctl", "position", "--player=spotify"])
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
    artist = escape_pango(meta["artist"])
    title = escape_pango(meta["title"])
    current = format_time(meta["position"])
    total = format_time(meta["length"])
    filled, empty = build_progress_bar(meta["position"], meta["length"], 10)
    return (
        f"<span foreground=\"#FFFFFF\"><b>{title}</b></span>\n"
        f"<span foreground=\"#F0E7AA\"><i>{artist}</i></span>\n"
        f"<span foreground=\"#FFFFFF\">{current}</span> "
        f"<span foreground=\"#CCC5C0\">{empty}</span>"
        f"<span foreground=\"#4B5F7D\">{filled}</span> "
        f"<span foreground=\"#FFFFFF\">{total}</span>\n"
        f"<span size='x-small' foreground='#AAAAAA'>🎧 spotify\n🖱 click → play/pause ou abrir\n🖱 scroll → volume +/-\n🖱 right-click → opções</span>"
    )

def print_json(text, tooltip, player_class):
    sys.stdout.write(json.dumps({
        "text": text,
        "tooltip": tooltip,
        "class": player_class
    }) + "\n")
    sys.stdout.flush()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--click":
        if is_spotify_running():
            toggle_play_pause()
        else:
            launch_spotify()
        sys.exit(0)

    scroll_artist = 0
    scroll_title = 0
    last_meta = None

    while True:
        if not is_spotify_running():
            print_json(f"{ICON} Spotify", "Clique para abrir Spotify", "stopped")
            time.sleep(1)
            continue

        meta = get_metadata()
        if not meta:
            print_json(f"{ICON} Spotify", " ", "paused")
            time.sleep(1)
            continue

        status_icon = "󰏤" if meta["status"] == "paused" else " "
        key = (meta["artist"], meta["title"])
        if key != last_meta:
            scroll_artist = 0
            scroll_title = 0
            last_meta = key

        artist = escape_pango(meta["artist"])
        title = escape_pango(meta["title"])
        artist_disp = marquee(artist, scroll_artist, MAX_CHAR) if len(artist) > MAX_CHAR else artist
        title_disp = marquee(title, scroll_title, MAX_CHAR) if len(title) > MAX_CHAR else title
        if len(artist) > MAX_CHAR: scroll_artist += 1
        if len(title) > MAX_CHAR: scroll_title += 1

        display_text = f"<i>{artist_disp}</i> • <b>{title_disp}</b>"
        text = f"{ICON} {status_icon} {display_text}"
        tooltip = build_tooltip(meta)
        print_json(text, tooltip, meta["status"])
        time.sleep(SCROLL_DELAY)

if __name__ == "__main__":
    main()
