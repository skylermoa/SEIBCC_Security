import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta

class DraggableLabel(tk.Label):
    """A label that can be dragged with the mouse."""

    def __init__(self, master, text, **kwargs):
        super().__init__(master, text=text, bd=1, relief="raised", padx=5, pady=5, **kwargs)
        self.text = text
        self.bind("<ButtonPress-1>", self.on_start)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.bind("<Double-Button-1>", self.on_double_click)
        self._drag_data = {"x": 0, "y": 0}
        self._is_dragging = False

    def on_start(self, event):

    def on_double_click(self, event):
        """Show client info when label is double-clicked."""
        if hasattr(self.master, "show_client_info"):
            self.master.show_client_info(self)

        self.bed_var = tk.StringVar()
        tk.Label(self, text="Bed Section:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.bed_var).grid(row=2, column=1, padx=5, pady=5)

        tk.Checkbutton(self, text="15-minute checks", variable=self.checks_var).grid(row=3, columnspan=2, sticky="w", padx=5, pady=5)
        tk.Label(self, text="Approved Contacts:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.contacts_var).grid(row=4, column=1, padx=5, pady=5)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
            "bed": self.bed_var.get().strip(),
class ClientInfoDialog(tk.Toplevel):
    """Popup to display a client's details."""

    def __init__(self, master, info):
        super().__init__(master)
        ttk.Combobox(
        entry_width = 20
        tk.Entry(self, textvariable=self.name_var, width=entry_width).grid(row=0, column=1, padx=5, pady=5)
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=1, column=1, padx=5, pady=5)

        tk.Entry(self, textvariable=self.bed_var, width=entry_width).grid(row=2, column=1, padx=5, pady=5)
        self.contacts_text.grid(row=4, column=1, padx=5, pady=5)
            "contacts": self.contacts_text.get("1.0", tk.END).strip(),
    """Popup to display and edit a client's details."""
        self.master = master
        self.info = info
        self.name_var = tk.StringVar(value=info.get("name", ""))
        self.gender_var = tk.StringVar(value=info.get("gender", ""))
        self.bed_var = tk.StringVar(value=info.get("bed", ""))
        self.checks_var = tk.BooleanVar(value=info.get("checks", False))

        entry_width = 20
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.name_var, width=entry_width).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.gender_var,
            values=["Male", "Female"],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Bed Section:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.bed_var, width=entry_width).grid(row=2, column=1, padx=5, pady=5)

        tk.Checkbutton(self, text="15-minute checks", variable=self.checks_var).grid(row=3, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(self, text="Approved Contacts:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.contacts_text = tk.Text(self, height=4, width=20)
        self.contacts_text.grid(row=4, column=1, padx=5, pady=5)
        self.contacts_text.insert("1.0", info.get("contacts", ""))

        button_frame = tk.Frame(self)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Discharge", fg="white", bg="red", command=self._discharge).pack(side=tk.LEFT)

    def _save(self):
        new_data = {
            "name": self.name_var.get().strip(),
            "gender": self.gender_var.get().strip(),
            "bed": self.bed_var.get().strip(),
            "checks": self.checks_var.get(),
            "contacts": self.contacts_text.get("1.0", tk.END).strip(),
        }
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

        self._schedule_checks()
        # Store the offset of the mouse inside the widget
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._is_dragging = True
        self.lift()

    def on_drag(self, event):

        if not self._is_dragging:
            return
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y)

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


class AddClientDialog(tk.Toplevel):
    """Popup window to gather client information."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Add Client")
        self.resizable(False, False)
        self.on_submit = on_submit

        self.name_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.checks_var = tk.BooleanVar()
        self.contacts_var = tk.StringVar()

        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.gender_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Checkbutton(self, text="15-minute checks", variable=self.checks_var).grid(row=2, columnspan=2, sticky="w", padx=5, pady=5)

        tk.Label(self, text="Approved Contacts:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self, textvariable=self.contacts_var).grid(row=3, column=1, padx=5, pady=5)

        button_frame = tk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Add", command=self._submit).pack(side=tk.RIGHT)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self):

        data = {
            "name": self.name_var.get().strip(),
            "gender": self.gender_var.get().strip(),
        }

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
            "checks": self.checks_var.get(),
            "contacts": self.contacts_var.get().strip(),
        }
        self.on_submit(data)
        self.destroy()


class CrisisCenterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crisis Center")
        self.geometry("900x600")
        self.clients = []
        self.locations = [
            "Group Room",
            "Asleep",
            "Medical",
            "Case Manager",
            "Patio",
            "Away from Center",
        ]
        self.location_contents = {}
        self._build_ui()

    def _build_ui(self):
        # Client controls
        control_frame = tk.Frame(self)
        control_frame.pack(fill=tk.X, pady=5)
        tk.Button(control_frame, text="Add Client", command=self.show_add_dialog).pack(side=tk.LEFT, padx=5)

        # Main frames
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.client_area = tk.Frame(main_frame, width=200, bg="lightgrey")
        self.client_area.pack(side=tk.LEFT, fill=tk.Y)
        location_frame = tk.Frame(main_frame)
        location_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            "name": name,
            "bed": data.get("bed", ""),
        self.location_frames = {}
        rows, cols = 2, 3
        for i, loc in enumerate(self.locations):
            row = i // cols
            col = i % cols
            frame = tk.Frame(location_frame, width=200, height=150, bd=2, relief="groove")
        self.log(f"INTAKE {name}")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            label = tk.Label(frame, text=loc)
            label.pack(side=tk.TOP)
            self.location_frames[loc] = frame
            label.pack(side=tk.TOP, anchor="w")
            holder = tk.Frame(frame)
            holder.pack(fill=tk.BOTH, expand=True)
            self.location_frames[loc] = holder
            self.location_contents[loc] = []

        for c in range(cols):
            location_frame.grid_columnconfigure(c, weight=1)
        for r in range(rows):
            location_frame.grid_rowconfigure(r, weight=1)

        # Log area
        self.log_text = tk.Text(self, height=10, state="disabled")
        self.log_text.pack(fill=tk.X, pady=5)

    def show_add_dialog(self):
        """Open the dialog to add a new client."""
        AddClientDialog(self, self.add_client)

    def add_client(self, data):
        name = data.get("name", "").strip()
        if not name:
            messagebox.showwarning("Input Error", "Client name cannot be empty")
            return
        label = DraggableLabel(self, name)
        label.current_location = None
        label.place(in_=self.client_area, x=10, y=30 * len(self.clients))
        gender = data.get("gender", "").strip()
        if not name or not gender:
            messagebox.showwarning(
                "Input Error", "Name and gender are required"
            )
            return
        label = DraggableLabel(self, name)
        label.current_location = None
        label.place(in_=self.client_area, x=5, y=30 * len(self.clients))
        client_info = {
            "label": label,
            "gender": data.get("gender", ""),
            "checks": data.get("checks", False),
            "contacts": data.get("contacts", ""),
        }
        self.clients.append(client_info)
        self._refresh_client_area()

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
        for key in ["gender", "bed", "checks", "contacts"]:
            if client.get(key) != new_data.get(key):
                changes.append(f"{key} changed")
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

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
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

        # Check if dropped in a defined location
        for location, frame in self.location_frames.items():
            x1, y1 = frame.winfo_rootx(), frame.winfo_rooty()
            x2, y2 = x1 + frame.winfo_width(), y1 + frame.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                self._move_to_location(widget, location)
                return

        # Not dropped on a location - return to client area
        if getattr(widget, "current_location", None):
            self.location_contents[widget.current_location].remove(widget)
            self._refresh_location(widget.current_location)
            widget.current_location = None
        self._refresh_client_area(widget)

    def _move_to_location(self, widget, location):
        """Place widget into the given location frame."""
        prev_location = getattr(widget, "current_location", None)
        if prev_location == location:
            # Already here, do not log again
            self._refresh_location(location)
            return
        if prev_location:
            self.location_contents[prev_location].remove(widget)
            self._refresh_location(prev_location)

        frame = self.location_frames[location]
        widget.current_location = location
        self.location_contents[location].append(widget)

        widget.place(in_=frame, x=5, y=20 * (len(self.location_contents[location]) - 1))
        widget.place(in_=frame, x=10, y=20 * (len(self.location_contents[location]) - 1))
        widget.place(in_=frame, x=5, y=20 * (len(self.location_contents[location]) - 1))

        self.log(f"{widget.text}'s location is {location}")

    def _refresh_location(self, location):
        """Reposition widgets in a location after changes."""
        frame = self.location_frames[location]
        for i, w in enumerate(self.location_contents[location]):

            w.place(in_=frame, x=5, y=20 * i)
            w.place(in_=frame, x=10, y=20 * i)
    def _refresh_client_area(self, widget=None):
        """Reposition widgets with no location in the client area."""
        unplaced = [c["label"] for c in self.clients if c["label"].current_location is None]
        if widget and widget not in unplaced:
            unplaced.append(widget)
        for i, w in enumerate(unplaced):
            w.place(in_=self.client_area, x=5, y=30 * i)
            w.place(in_=self.client_area, x=10, y=30 * i)
            w.place(in_=self.client_area, x=5, y=30 * i)


    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)


if __name__ == "__main__":
    app = CrisisCenterApp()
    app.mainloop()

