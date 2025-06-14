import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

MIN_ROOM_WIDTH = 150
MIN_ROOM_HEIGHT = 120
MIN_LOG_HEIGHT = 120

PROPERTY_KEYS = ["Tray", "Medical", "Bin", "Sharps", "Hot Room"]



class DraggableLabel(tk.Label):
    """A label that can be dragged with the mouse."""

    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text,
            bd=1,
            relief="raised",
            padx=5,
            pady=5,
            width=15,
            anchor="center",
            justify="center",
            wraplength=120,
            **kwargs,
        )
        self.text = text
        self.bind("<ButtonPress-1>", self.on_start)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.bind("<Double-Button-1>", self.on_double_click)
        self._drag_data = {"x": 0, "y": 0}
        self._is_dragging = False

    def on_start(self, event):
        """Begin dragging the label."""
        # Store the offset of the mouse inside the widget
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._is_dragging = True
        if hasattr(self.master, "start_drag"):
            self.master.start_drag(self)
        self.lift()

    def on_drag(self, event):
        """Handle the label being dragged."""
        if not self._is_dragging:
            return
        new_x = (
            event.x_root - self.master.winfo_rootx() - self._drag_data["x"]
        )
        new_y = (
            event.y_root - self.master.winfo_rooty() - self._drag_data["y"]
        )
        self.place(in_=self.master, x=new_x, y=new_y)

    def on_drop(self, event):
        self._is_dragging = False
        self.master.on_drop(self, event)

    def on_double_click(self, event):
        """Show client info when label is double-clicked."""
        if hasattr(self.master, "show_client_info"):
            self.master.show_client_info(self)


class AddClientDialog(tk.Toplevel):
    """Popup window to gather client information."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Add Client")
        self.geometry("300x150")
        self.resizable(True, True)
        self.on_submit = on_submit

        self.name_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        # Add-client dialog only collects name and gender; other details are
        # edited later in the client info popup

        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_width = 20
        tk.Entry(self, textvariable=self.name_var, width=entry_width).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=1, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Add", command=self._submit).pack(side=tk.RIGHT)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self):
        name = self.name_var.get().strip()
        gender = self.gender_var.get().strip()
        if not name or not gender:
            messagebox.showwarning(
                "Input Error", "Name and gender are required"
            )
            return

        data = {
            "name": name,
            "gender": gender,
        }
        self.on_submit(data)
        self.destroy()


class EventDialog(tk.Toplevel):
    """Popup to log visitor or incident events."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Event")
        self.geometry("350x300")
        self.resizable(True, True)
        self.on_submit = on_submit

        self.type_var = tk.StringVar()

        tk.Label(self, text="Type:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.type_var,
            values=["Visitor", "Incident"],
            state="readonly",
            width=18,
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Comments:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        self.comment_text = tk.Text(self, width=25, height=6)
        self.comment_text.grid(row=1, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Add", command=self._submit).pack(side=tk.RIGHT)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self):
        ev_type = self.type_var.get().strip()
        comments = self.comment_text.get("1.0", tk.END).strip()
        if not ev_type:
            messagebox.showwarning("Input Error", "Please select an event type")
            return
        self.on_submit(ev_type, comments)
        self.destroy()


class ReturnTimeDialog(tk.Toplevel):
    """Popup to select an estimated return time."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Estimated Return")
        self.geometry("250x120")
        self.resizable(True, True)
        self.result = None

        times = [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
        self.var = tk.StringVar(value=times[0])

        tk.Label(self, text="Return Time:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(self, values=times, textvariable=self.var, state="readonly", width=18).grid(row=0, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="OK", command=self._ok).pack(side=tk.RIGHT)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _ok(self):
        self.result = self.var.get()
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class ClientInfoDialog(tk.Toplevel):
    """Popup to display and edit a client's details."""

    def __init__(self, master, info):
        super().__init__(master)
        self.master = master
        self.info = info
        self.title(info.get("name", "Client Info"))
        self.geometry("350x500")
        self.resizable(True, True)

        self.name_var = tk.StringVar(value=info.get("name", ""))
        self.gender_var = tk.StringVar(value=info.get("gender", ""))
        self.bed_var = tk.StringVar(value=info.get("bed", ""))
        self.checks_var = tk.BooleanVar(value=info.get("checks", False))
        self.return_time = info.get("return_time")
        self.property_vars = {
            k: tk.BooleanVar(value=info.get("property", {}).get(k, False))
            for k in PROPERTY_KEYS
        }

        entry_width = 20
        row = 0
        tk.Label(self, text="Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.name_var, width=entry_width).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Gender:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self, text="Bed Section:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.bed_var, width=entry_width).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Checkbutton(self, text="15-minute checks", variable=self.checks_var).grid(row=row, columnspan=2, sticky="w", padx=5, pady=5)
        row += 1

        tk.Label(self, text="Approved Contacts:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        self.contacts_text = tk.Text(self, height=4, width=20)
        self.contacts_text.grid(row=row, column=1, padx=5, pady=5)
        self.contacts_text.insert("1.0", info.get("contacts", ""))
        row += 1

        tk.Label(self, text="Property:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        prop_frame = tk.Frame(self)
        prop_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        for p in PROPERTY_KEYS:
            tk.Checkbutton(prop_frame, text=p, variable=self.property_vars[p]).pack(anchor="w")
        row += 1

        if self.return_time is not None:
            tk.Label(self, text="Est. Return:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            times = [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
            self.return_var = tk.StringVar(value=self.return_time)
            ttk.Combobox(
                self,
                values=times,
                textvariable=self.return_var,
                state="readonly",
                width=entry_width - 2,
            ).grid(row=row, column=1, padx=5, pady=5)
            row += 1

        button_frame = tk.Frame(self)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Discharge", fg="white", bg="red", command=self._discharge).pack(side=tk.LEFT)

        self.grab_set()

    def _save(self):
        new_data = {
            "name": self.name_var.get().strip(),
            "gender": self.gender_var.get().strip(),
            "bed": self.bed_var.get().strip(),
            "checks": self.checks_var.get(),
            "contacts": self.contacts_text.get("1.0", tk.END).strip(),
            "property": {k: var.get() for k, var in self.property_vars.items()},
        }
        if hasattr(self, "return_var"):
            new_data["return_time"] = self.return_var.get()
        self.master.update_client_info(self.info, new_data)
        self.destroy()

    def _discharge(self):
        confirm = messagebox.askyesno(
            "Discharge",
            "Have you gathered all client property, spoken with case management and medical, and are ready to discharge?",
        )
        if confirm:
            self.master.discharge_client(self.info)
            self.destroy()


class CrisisCenterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crisis Center")
        self.geometry("900x600")
        self.label_spacing = 35
        self.clients = []
        self.locations = [
            "Group Room",
            "In Bed",
            "Medical",
            "Case Manager",
            "Patio",
            "Shower",
            "Away from Center",
        ]
        self.location_contents = {}
        self._build_ui()
        self._schedule_checks()

    def _update_scrollregion(self, location):
        canvas = self.location_canvases.get(location)
        if canvas:
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                width = max(MIN_ROOM_WIDTH, bbox[2] + 10)
                height = max(MIN_ROOM_HEIGHT, bbox[3] + 10)
                canvas.configure(scrollregion=bbox, width=width, height=height)
            else:
                canvas.configure(width=MIN_ROOM_WIDTH, height=MIN_ROOM_HEIGHT)

    def _build_ui(self):
        # Client controls
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, pady=5)
        tk.Button(control_frame, text="Add Client", command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Event", command=self.show_event_dialog).pack(side=tk.LEFT, padx=5)

        # Main frames
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.client_area = tk.Frame(main_frame, width=200, bg="lightgrey")
        self.client_area.pack(side=tk.LEFT, fill=tk.Y)
        location_frame = tk.Frame(main_frame)
        location_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.location_frames = {}
        self.location_canvases = {}
        self.location_contents = {}
        # Track the canvas window item for each label
        self.label_windows = {}
        cols = 3
        rows = (len(self.locations) + cols - 1) // cols
        configured_rows = set()
        configured_cols = set()
        for i, loc in enumerate(self.locations):
            row = i // cols
            col = i % cols
            frame = tk.Frame(location_frame, bd=2, relief="groove")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            label = tk.Label(frame, text=loc)
            label.pack(side=tk.TOP, anchor="w")

            canvas = tk.Canvas(frame)
            canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.configure(yscrollcommand=scrollbar.set)

            self.location_frames[loc] = frame
            self.location_canvases[loc] = canvas
            self.location_contents[loc] = []

            if row not in configured_rows:
                location_frame.grid_rowconfigure(row, weight=1, minsize=MIN_ROOM_HEIGHT)
                configured_rows.add(row)
            if col not in configured_cols:
                location_frame.grid_columnconfigure(col, weight=1, minsize=MIN_ROOM_WIDTH)
                configured_cols.add(col)
            self._update_scrollregion(loc)


        # Log area with scrollbar
        log_frame = tk.Frame(self, height=MIN_LOG_HEIGHT)
        log_frame.pack(fill=tk.BOTH, pady=5)
        log_frame.pack_propagate(False)
        self.log_text = tk.Text(log_frame, height=10, state="disabled")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def show_add_dialog(self):
        """Open the dialog to add a new client."""
        AddClientDialog(self, self.add_client)

    def show_event_dialog(self):
        """Open the dialog to log an event."""
        EventDialog(self, self.add_event)

    def add_client(self, data):
        name = data.get("name", "").strip()
        gender = data.get("gender", "").strip()
        if not name or not gender:
            messagebox.showwarning(
                "Input Error", "Name and gender are required"
            )
            return
        label = DraggableLabel(self, name)
        label.current_location = None
        label.place(in_=self.client_area, x=5, y=self.label_spacing * len(self.clients))
        client_info = {
            "name": name,
            "label": label,
            "gender": gender,
            "bed": "",
            "checks": False,
            "contacts": "",
            "property": {k: False for k in PROPERTY_KEYS},
            "return_time": None,
        }
        self.clients.append(client_info)
        self._refresh_client_area()
        self.log(f"INTAKE {name}")

    def add_event(self, ev_type, comments):
        """Log an event from the event dialog."""
        if comments:
            self.log(f"Event {ev_type}: {comments}")
        else:
            self.log(f"Event {ev_type}")

    def start_drag(self, widget):
        """Prepare a label for dragging by removing it from its current container."""
        if widget.current_location:
            loc = widget.current_location
            widget.drag_origin = loc
            canvas = self.location_canvases[loc]
            canvas.delete(self.label_windows.pop(widget, None))
            self.location_contents[loc].remove(widget)
            widget.current_location = None
            self._refresh_location(loc)
        else:
            widget.drag_origin = None
            self._refresh_client_area(exclude=widget)

    def on_drop(self, widget, event):
        # Check if dropped in a defined location
        for location, frame in self.location_frames.items():
            x1, y1 = frame.winfo_rootx(), frame.winfo_rooty()
            x2, y2 = x1 + frame.winfo_width(), y1 + frame.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                self._move_to_location(widget, location)
                return

        # Not dropped on a location - snap back to previous position
        origin = getattr(widget, "drag_origin", None)
        if origin:
            self._move_to_location(widget, origin)
        else:
            widget.current_location = None
            self._refresh_client_area()

    def _move_to_location(self, widget, location):
        """Place widget into the given location frame."""
        prev_location = getattr(widget, "current_location", None)
        origin = getattr(widget, "drag_origin", prev_location)
        if prev_location is None:
            prev_location = origin
        client = self._find_client(widget)
        if prev_location == location:
            # If the widget was removed during drag, reinsert it
            if widget not in self.location_contents.get(location, []):
                canvas = self.location_canvases[location]
                self.location_contents[location].append(widget)
                window_id = canvas.create_window(0, 0, window=widget, anchor="nw")
                self.label_windows[widget] = window_id
                widget.current_location = location
            self._refresh_location(location)
            return

        if location == "Away from Center":
            dlg = ReturnTimeDialog(self)
            self.wait_window(dlg)
            if dlg.result is None:
                if prev_location:
                    self._refresh_location(prev_location)
                else:
                    self._refresh_client_area()
                return
            if client is not None:
                client["return_time"] = dlg.result
        elif prev_location == "Away from Center" and client is not None:
            self._handle_return(widget, client)

        if prev_location and widget in self.location_contents.get(prev_location, []):
            canvas = self.location_canvases[prev_location]
            canvas.delete(self.label_windows.pop(widget, None))
            self.location_contents[prev_location].remove(widget)
            self._refresh_location(prev_location)

        canvas = self.location_canvases[location]
        widget.current_location = location
        self.location_contents[location].append(widget)
        window_id = canvas.create_window(0, 0, window=widget, anchor="nw")
        self.label_windows[widget] = window_id
        self._refresh_location(location)
        if location == "Away from Center" and client is not None:
            self.log(f"{widget.text}'s location is {location} (return {client['return_time']})")
        else:
            self.log(f"{widget.text}'s location is {location}")

    def _refresh_location(self, location):
        """Reposition widgets in a location after changes."""
        canvas = self.location_canvases[location]
        canvas.update_idletasks()
        max_rows = max(1, canvas.winfo_height() // self.label_spacing)
        for i, w in enumerate(self.location_contents[location]):
            w.update_idletasks()
            col = i // max_rows
            row = i % max_rows
            x = 5 + col * (w.winfo_reqwidth() + 10)
            y = self.label_spacing * row
            canvas.coords(self.label_windows[w], x, y)
        self._update_scrollregion(location)

    def _refresh_client_area(self, exclude=None):
        """Reposition widgets with no location in the client area."""
        unplaced = [c["label"] for c in self.clients if c["label"].current_location is None]
        if exclude and exclude in unplaced:
            unplaced.remove(exclude)
        for i, w in enumerate(unplaced):
            w.place(in_=self.client_area, x=5, y=self.label_spacing * i)

    def _find_client(self, widget):
        """Return the client dictionary for a label widget."""
        return next((c for c in self.clients if c["label"] is widget), None)

    def _handle_return(self, widget, client):
        """Handle a client returning from being away."""
        screening = messagebox.askyesno(
            "Client Return",
            f"Was a security screening completed for {client['name']}?",
        )
        note = "completed" if screening else "NOT completed"
        self.log(f"Security screening for {client['name']} {note}")
        client.pop("return_time", None)

    def show_client_info(self, label):
        """Display client information in a popup."""
        info = next((c for c in self.clients if c["label"] is label), None)
        if not info:
            return
        ClientInfoDialog(self, info)

    def update_client_info(self, client, new_data):
        """Update a client's details and log any changes."""
        changes = []
        if client["name"] != new_data["name"]:
            changes.append(f"name from {client['name']} to {new_data['name']}")
            client["label"].config(text=new_data["name"])
            client["label"].text = new_data["name"]
        for key in ["gender", "bed", "checks", "contacts", "return_time"]:
            if client.get(key) != new_data.get(key):
                changes.append(f"{key} changed")
        if "property" in new_data:
            for p, val in new_data["property"].items():
                if client.get("property", {}).get(p) != val:
                    changes.append(f"property {p} changed")
        client.update(new_data)
        if changes:
            self.log(f"Updated {client['name']}'s info: " + "; ".join(changes))
        self._refresh_client_area()

    def discharge_client(self, client):
        """Remove a client from the system."""
        label = client["label"]
        if label.current_location:
            self.location_contents[label.current_location].remove(label)
            self._refresh_location(label.current_location)
        label.destroy()
        self.clients.remove(client)
        self.log(f"DISCHARGE {client['name']}")
        self._refresh_client_area()

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def _schedule_checks(self):
        """Schedule the next 15-minute check notifications."""
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
        """Prompt staff to perform 15-minute checks."""
        for client in self.clients:
            if client.get("checks"):
                messagebox.showinfo("15 Minute Check", f"Check on {client['name']}")
                self.log(f"15 minute check for {client['name']} complete")
        self._schedule_checks()


if __name__ == "__main__":
    app = CrisisCenterApp()
    app.mainloop()