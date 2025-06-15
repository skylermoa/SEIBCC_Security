
+61
-0

import json
import os
from datetime import datetime
from typing import List
from .constants import CLIENTS_FILE, LOG_DIR, PROPERTY_KEYS
from .models import Client


def save_clients(clients: List[Client]) -> None:
    data = []
    for c in clients:
        entry = {
            "name": c.name,
            "gender": c.gender,
            "bed": c.bed,
            "checks": c.checks,
            "contacts": c.contacts,
            "property": c.property,
            "return_time": c.return_time,
            "wakeup_time": c.wakeup_time,
            "location": c.label.current_location if c.label else None,
        }
        data.append(entry)
    with open(CLIENTS_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_clients() -> List[Client]:
    if not os.path.exists(CLIENTS_FILE):
        return []
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return []
    clients = []
    for info in data:
        c = Client(
            name=info.get("name", ""),
            gender=info.get("gender", ""),
            bed=info.get("bed", ""),
            checks=info.get("checks", False),
            contacts=info.get("contacts", ""),
            property={k: info.get("property", {}).get(k, False) for k in PROPERTY_KEYS},
            return_time=info.get("return_time"),
            wakeup_time=info.get("wakeup_time"),
        )
        c.location = info.get("location", "Group Room")
        clients.append(c)
    return clients


def append_log(timestamp: datetime, message: str) -> None:
    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%Y-%m-%d")
    dir_path = os.path.join(LOG_DIR, year, month)
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, f"{day}.txt")
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
