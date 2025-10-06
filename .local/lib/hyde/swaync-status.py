#!/usr/bin/python3

import json
import subprocess

ICON_DND_EMPTY = ""  # DND ativo, 0 notificações
ICON_DND_NEW   = ""  # DND ativo, com notificações não lidas
ICON_EMPTY     = ""  # DND desativado, 0 notificações
ICON_NEW       = ""  # DND desativado, com notificações não lidas

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ""

# Verifica DND
dnd_state = run("swaync-client --get-dnd")
dnd_enabled = dnd_state.lower() == "true"

# Verifica notificações 
count = run("swaync-client -c")
try:
    count = int(count)
except ValueError:
    count = 0

# Define ícone
if dnd_enabled:
    icon = ICON_DND_NEW if count > 0 else ICON_DND_EMPTY
else:
    icon = ICON_NEW if count > 0 else ICON_EMPTY

tooltip = f"{count} notificações não lidas"

print(json.dumps({
    "text": f"{count} {icon} ",
    "tooltip": tooltip,
    "class": ["dnd" if dnd_enabled else "normal"]
}))
