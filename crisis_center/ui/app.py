import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta

from ..constants import (
    APP_BG,
    BUTTON_BG,
    BUTTON_FG,
    BUTTON_PADX,
    BUTTON_PADY,
    BUTTON_FONT,
    LOCATION_BG,
    LOG_BG,
    MIN_LOG_HEIGHT,
    LOG_DIR,
    MIN_ROOM_HEIGHT,
    MIN_ROOM_WIDTH,
    DESKTOP_WIDTH,
    TABLET_WIDTH,
    APP_MIN_WIDTH,
    APP_MIN_HEIGHT,
    MAX_LABELS_PER_COLUMN,
    PROPERTY_KEYS,
    SHOWER_TIMEOUT_MS,
    BED_OPTIONS,
)
from ..models import Client
from ..persistence import save_clients, load_clients, append_log
from .widgets import DraggableLabel
from .dialogs import (
    AddClientDialog,
    EventDialog,
    ReturnTimeDialog,
    ClientInfoDialog,
)


class CrisisCenterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crisis Center")
        self.geometry("900x600")
        self.minsize(APP_MIN_WIDTH, APP_MIN_HEIGHT)
        self.configure(bg=APP_BG)
        self.label_spacing = 35
        self.clients: list[Client] = []
        self.locations = [
            "Group Room",
            "Bed",
            "Medical Office",
            "Case Manager Office",
            "Peer Support Office",
            "Shower",
            "Patio",
            "Away from Crisis Center",
        ]
        self.location_contents = {}
        self._build_ui()
        self._schedule_checks()
        self.bind("<Configure>", self._on_resize)

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1, minsize=MIN_LOG_HEIGHT)
        self.grid_columnconfigure(0, weight=1)

        control_frame = tk.Frame(self, bg=APP_BG)
        control_frame.grid(row=0, column=0, sticky="ew", pady=5)
        tk.Button(
            control_frame,
            text="Add Client",
            command=self.show_add_dialog,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side=tk.LEFT, padx=BUTTON_PADX, pady=BUTTON_PADY)
        tk.Button(
            control_frame,
            text="Event",
            command=self.show_event_dialog,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side=tk.LEFT, padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.location_frame = tk.Frame(self, bg=APP_BG)
        self.location_frame.grid(row=1, column=0, sticky="nsew")

        self.location_frames = {}
        self.location_holders = {}
        for loc in self.locations:
            frame = tk.Frame(self.location_frame, bd=2, relief="groove", bg=LOCATION_BG)
            label = tk.Label(frame, text=loc, font=("TkDefaultFont", 12, "bold"), bg=LOCATION_BG)
            label.pack(side=tk.TOP, anchor="w")
            holder = tk.Frame(frame, bg=LOCATION_BG)
            holder.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.location_frames[loc] = frame
            self.location_holders[loc] = holder
            self.location_contents[loc] = []

        self._layout_locations()

        log_frame = tk.Frame(self, bg=LOG_BG)
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word", bg=LOG_BG)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.load_clients()
        self.load_logs()

    def _layout_locations(self):
        width = self.winfo_width()
        if width <= 1:
            self.update_idletasks()
            width = self.winfo_width()
        if width >= DESKTOP_WIDTH:
            cols = 3
        elif width >= TABLET_WIDTH:
            cols = 2
        else:
            cols = 1
        cols = min(cols, len(self.locations))
        if getattr(self, "_loc_cols", None) == cols:
            return
        self._loc_cols = cols
        rows_needed = (len(self.locations) + cols - 1) // cols
        for r in range(rows_needed):
            self.location_frame.grid_rowconfigure(r, weight=1, minsize=MIN_ROOM_HEIGHT)
        for c in range(cols):
            self.location_frame.grid_columnconfigure(c, weight=1, minsize=MIN_ROOM_WIDTH)
        for i, loc in enumerate(self.locations):
            row = i // cols
            col = i % cols
            frame = self.location_frames[loc]
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
        for loc in self.locations:
            self._refresh_location(loc)

    def _on_resize(self, event):
        if event.widget is self:
            self._layout_locations()

    def show_add_dialog(self):
        AddClientDialog(self, self.add_client)

    def show_event_dialog(self):
        EventDialog(self, self.add_event)

    def add_client(self, data):
        name = data.get("name", "").strip()
        gender = data.get("gender", "").strip()
        if not name or not gender:
            messagebox.showwarning("Input Error", "Name and gender are required")
            return
        label = DraggableLabel(self, name)
        label.current_location = None
        client = Client(name=name, gender=gender, label=label, property={k: False for k in PROPERTY_KEYS})
        self.clients.append(client)
        self._move_to_location(label, "Group Room")
        self.log(f"INTAKE {name}")
        self.save_clients()

    def add_event(self, ev_type, comments):
        if comments:
            self.log(f"Event {ev_type}: {comments}")
        else:
            self.log(f"Event {ev_type}")

    def start_drag(self, widget):
        if widget.current_location:
            loc = widget.current_location
            widget.drag_origin = loc
            widget.grid_forget()
            self.location_contents[loc].remove(widget)
            widget.current_location = None
            self._refresh_location(loc)
        else:
            widget.drag_origin = None

    def on_drop(self, widget, event):
        for location, frame in self.location_frames.items():
            x1, y1 = frame.winfo_rootx(), frame.winfo_rooty()
            x2, y2 = x1 + frame.winfo_width(), y1 + frame.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                self._move_to_location(widget, location)
                return
        origin = getattr(widget, "drag_origin", None)
        self._move_to_location(widget, origin or "Group Room")

    def _move_to_location(self, widget, location, log_move=True):
        if location not in self.location_holders:
            location = "Group Room"
        prev_location = getattr(widget, "current_location", None)
        origin = getattr(widget, "drag_origin", prev_location)
        if prev_location is None:
            prev_location = origin
        client = self._find_client(widget)
        if prev_location == location:
            if widget not in self.location_contents.get(location, []):
                self.location_contents[location].append(widget)
            widget.current_location = location
            self._refresh_location(location)
            return
        if location == "Away from Crisis Center":
            dlg = ReturnTimeDialog(self)
            self.wait_window(dlg)
            if dlg.result is None:
                if prev_location:
                    self._move_to_location(widget, prev_location, log_move=False)
                else:
                    self._move_to_location(widget, "Group Room", log_move=False)
                return
            if client is not None:
                client.return_time = dlg.result
        elif prev_location == "Away from Crisis Center" and client is not None:
            self._handle_return(widget, client)
        if location == "Shower" and client is not None:
            self._start_shower_timer(client)
        elif prev_location == "Shower" and client is not None:
            self._cancel_shower_timer(client)
        if prev_location and widget in self.location_contents.get(prev_location, []):
            widget.grid_forget()
            self.location_contents[prev_location].remove(widget)
            self._refresh_location(prev_location)
        widget.current_location = location
        self.location_contents[location].append(widget)
        self._refresh_location(location)
        if log_move:
            if location == "Away from Crisis Center" and client is not None:
                self.log(f"{widget.text}'s location is {location} (return {client.return_time})")
            else:
                self.log(f"{widget.text}'s location is {location}")
        self.save_clients()

    def _refresh_location(self, location):
        holder = self.location_holders[location]
        for child in holder.winfo_children():
            child.grid_forget()
        labels = self.location_contents.get(location, [])
        if getattr(self, "_loc_cols", 1) == 1:
            max_rows = len(labels) or 1
            cols = 1
        else:
            max_rows = MAX_LABELS_PER_COLUMN
            cols = (len(labels) + max_rows - 1) // max_rows
        for c in range(cols):
            holder.grid_columnconfigure(c, weight=1)
        for r in range(max_rows):
            holder.grid_rowconfigure(r, weight=1)
        for i, lbl in enumerate(labels):
            row = i % max_rows
            col = i // max_rows
            lbl.grid(in_=holder, row=row, column=col, padx=2, pady=2, sticky="nsew")

    def _find_client(self, widget):
        return next((c for c in self.clients if c.label is widget), None)

    def _handle_return(self, widget, client: Client):
        screening = messagebox.askyesno(
            "Client Return",
            f"Was a security screening completed for {client.name}?",
        )
        note = "completed" if screening else "NOT completed"
        self.log(f"Security screening for {client.name} {note}")
        client.return_time = None
        self._cancel_shower_timer(client)

    def _start_shower_timer(self, client: Client):
        self._cancel_shower_timer(client)
        client.shower_after = self.after(
            SHOWER_TIMEOUT_MS, lambda c=client: self._shower_time_up(c)
        )

    def _cancel_shower_timer(self, client: Client):
        timer = client.shower_after
        if timer:
            self.after_cancel(timer)
            client.shower_after = None

    def _shower_time_up(self, client: Client):
        client.shower_after = None
        if client.label.current_location == "Shower":
            messagebox.showinfo(
                "Shower Time",
                f"Tell {client.name} their shower time has ended.",
            )

    def show_client_info(self, label):
        info = self._find_client(label)
        if not info:
            return
        ClientInfoDialog(self, info.__dict__)

    def update_client_info(self, client: Client, new_data):
        changes = []
        if client.name != new_data["name"]:
            changes.append(f"name from {client.name} to {new_data['name']}")
            client.label.config(text=new_data["name"])
            client.label.text = new_data["name"]
        for key in ["gender", "bed", "checks", "contacts", "return_time", "wakeup_time"]:
            if getattr(client, key) != new_data.get(key):
                changes.append(f"{key} changed")
        if "property" in new_data:
            for p, val in new_data["property"].items():
                if client.property.get(p) != val:
                    changes.append(f"property {p} changed")
        client.name = new_data["name"]
        client.gender = new_data["gender"]
        client.bed = new_data["bed"]
        client.checks = new_data["checks"]
        client.contacts = new_data["contacts"]
        client.wakeup_time = new_data["wakeup_time"]
        client.property = new_data["property"]
        if "return_time" in new_data:
            client.return_time = new_data["return_time"]
        if changes:
            self.log(f"Updated {client.name}'s info: " + "; ".join(changes))
        self.save_clients()

    def discharge_client(self, client: Client):
        label = client.label
        if label.current_location:
            self.location_contents[label.current_location].remove(label)
            self._refresh_location(label.current_location)
        label.destroy()
        self.clients.remove(client)
        self.log(f"DISCHARGE {client.name}")
        self.save_clients()

    def available_beds(self, exclude=None):
        taken = {
            c.bed for c in self.clients if c.bed and c.bed != exclude
        }
        return [b for b in BED_OPTIONS if b not in taken]

    def log(self, message):
        timestamp = datetime.now()
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{ts_str}] {message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)
        append_log(timestamp, message)

    def save_clients(self):
        save_clients(self.clients)

    def load_clients(self):
        data = load_clients()
        for c in data:
            label = DraggableLabel(self, c.name)
            label.current_location = None
            c.label = label
            self.clients.append(c)
            location = getattr(c, "location", "Group Room")
            self._move_to_location(label, location, log_move=False)

    def load_logs(self):
        cutoff = datetime.now() - timedelta(hours=24)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        dates = {cutoff.date(), datetime.now().date()}
        for d in sorted(dates):
            path = os.path.join(
                LOG_DIR,
                d.strftime("%Y"),
                d.strftime("%m"),
                f"{d.strftime('%Y-%m-%d')}.txt",
            )
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            ts_str = line.split("]", 1)[0].strip("[")
                            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            continue
                        if ts >= cutoff:
                            self.log_text.insert(tk.END, line)
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def _schedule_checks(self):
        now = datetime.now()
        next_minute = ((now.minute // 15) + 1) * 15
        hour = now.hour
        if next_minute >= 60:
            next_minute = 0
            hour = (hour + 1) % 24
        next_time = now.replace(hour=hour, minute=next_minute, second=0, microsecond=0)
        delay = (next_time - now).total_seconds() * 1000
        self.after(int(delay), self._run_checks)

    def _run_checks(self):
        for client in self.clients:
            if client.checks:
                messagebox.showinfo("15 Minute Check", f"Check on {client.name}")
                self.log(f"15 minute check for {client.name} complete")
        self._schedule_checks()
