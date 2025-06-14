import tkinter as tk
from tkinter import simpledialog, messagebox


class DraggableLabel(tk.Label):
    """A label that can be dragged with the mouse."""

    def __init__(self, master, text, **kwargs):
        super().__init__(master, text=text, bd=1, relief="raised", padx=5, pady=5, **kwargs)
        self.text = text
        self.bind("<ButtonPress-1>", self.on_start)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self._drag_data = {"x": 0, "y": 0}
        self._is_dragging = False

    def on_start(self, event):
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

        self.location_frames = {}
        rows, cols = 2, 3
        for i, loc in enumerate(self.locations):
            row = i // cols
            col = i % cols
            frame = tk.Frame(location_frame, width=200, height=150, bd=2, relief="groove")
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            label = tk.Label(frame, text=loc)
            label.pack(side=tk.TOP)
            self.location_frames[loc] = frame
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
        client_info = {
            "label": label,
            "gender": data.get("gender", ""),
            "checks": data.get("checks", False),
            "contacts": data.get("contacts", ""),
        }
        self.clients.append(client_info)
        self._refresh_client_area()

    def on_drop(self, widget, event):
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
        if getattr(widget, "current_location", None):
            self.location_contents[widget.current_location].remove(widget)
            self._refresh_location(widget.current_location)

        frame = self.location_frames[location]
        widget.current_location = location
        self.location_contents[location].append(widget)
        widget.place(in_=frame, x=10, y=20 * (len(self.location_contents[location]) - 1))
        self.log(f"{widget.text}'s location is {location}")

    def _refresh_location(self, location):
        """Reposition widgets in a location after changes."""
        frame = self.location_frames[location]
        for i, w in enumerate(self.location_contents[location]):
            w.place(in_=frame, x=10, y=20 * i)

    def _refresh_client_area(self, widget=None):
        """Reposition widgets with no location in the client area."""
        unplaced = [c["label"] for c in self.clients if c["label"].current_location is None]
        if widget and widget not in unplaced:
            unplaced.append(widget)
        for i, w in enumerate(unplaced):
            w.place(in_=self.client_area, x=10, y=30 * i)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)


if __name__ == "__main__":
    app = CrisisCenterApp()
    app.mainloop()

