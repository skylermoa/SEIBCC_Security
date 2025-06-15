from tkinter import (
    Toplevel, messagebox, ttk, Frame, Label, Entry, Text, Scrollbar,
    Checkbutton, Button, StringVar, BooleanVar
)
from ..constants import BUTTON_BG, BUTTON_FG, BUTTON_PADX, BUTTON_PADY, BUTTON_FONT, PROPERTY_KEYS


class AddClientDialog(Toplevel):
    """Popup window to gather client information."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Add Client")
        self.geometry("300x150")
        self.resizable(True, True)
        self.transient(master)
        self.update_idletasks()
        x = master.winfo_rootx() + 50
        y = master.winfo_rooty() + 50
        self.geometry(f"+{x}+{y}")
        self.on_submit = on_submit

        self.name_var = StringVar()
        self.gender_var = StringVar()

        Label(self, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        entry_width = 20
        Entry(self, textvariable=self.name_var, width=entry_width).grid(row=0, column=1, padx=5, pady=5)

        Label(self, text="Gender:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.gender_var,
            values=[
                "Male",
                "Female",
                "Transgender Male",
                "Transgender Female",
            ],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=1, column=1, padx=5, pady=5)

        button_frame = Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)
        Button(
            button_frame,
            text="Add",
            command=self._submit,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self):
        name = self.name_var.get().strip()
        gender = self.gender_var.get().strip()
        if not name or not gender:
            messagebox.showwarning("Input Error", "Name and gender are required")
            return
        data = {"name": name, "gender": gender}
        self.on_submit(data)
        self.destroy()


class EventDialog(Toplevel):
    """Popup to log visitor or incident events."""

    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Event")
        self.geometry("350x300")
        self.resizable(True, True)
        self.transient(master)
        self.update_idletasks()
        x = master.winfo_rootx() + 50
        y = master.winfo_rooty() + 50
        self.geometry(f"+{x}+{y}")
        self.on_submit = on_submit

        self.type_var = StringVar()

        Label(self, text="Type:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.type_var,
            values=["Visitor", "Incident", "Other"],
            state="readonly",
            width=18,
        ).grid(row=0, column=1, padx=5, pady=5)

        Label(self, text="Comments:").grid(row=1, column=0, sticky="ne", padx=5, pady=5)
        comment_frame = Frame(self)
        comment_frame.grid(row=1, column=1, padx=5, pady=5)
        self.comment_text = Text(comment_frame, width=25, height=6, wrap="word")
        scroll = Scrollbar(comment_frame, command=self.comment_text.yview)
        self.comment_text.configure(yscrollcommand=scroll.set)
        self.comment_text.pack(side="left", fill="both")
        scroll.pack(side="right", fill="y")

        button_frame = Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)
        Button(
            button_frame,
            text="Add",
            command=self._submit,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self):
        ev_type = self.type_var.get().strip()
        comments = self.comment_text.get("1.0", "end").strip()
        if not ev_type:
            messagebox.showwarning("Input Error", "Please select an event type")
            return
        self.on_submit(ev_type, comments)
        self.destroy()


class ReturnTimeDialog(Toplevel):
    """Popup to select an estimated return time."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Estimated Return")
        self.geometry("250x120")
        self.resizable(True, True)
        self.transient(master)
        self.update_idletasks()
        x = master.winfo_rootx() + 50
        y = master.winfo_rooty() + 50
        self.geometry(f"+{x}+{y}")
        self.result = None

        times = [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
        self.var = StringVar(value=times[0])

        Label(self, text="Return Time:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(self, values=times, textvariable=self.var, state="readonly", width=18).grid(row=0, column=1, padx=5, pady=5)

        btn_frame = Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        Button(
            btn_frame,
            text="Cancel",
            command=self._cancel,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)
        Button(
            btn_frame,
            text="OK",
            command=self._ok,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _ok(self):
        self.result = self.var.get()
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class ClientInfoDialog(Toplevel):
    """Popup to display and edit a client's details."""

    def __init__(self, master, info):
        super().__init__(master)
        self.master = master
        self.info = info
        self.title(info.get("name", "Client Info"))
        self.geometry("350x500")
        self.resizable(True, True)
        self.transient(master)
        self.update_idletasks()
        x = master.winfo_rootx() + 50
        y = master.winfo_rooty() + 50
        self.geometry(f"+{x}+{y}")

        self.name_var = StringVar(value=info.get("name", ""))
        self.gender_var = StringVar(value=info.get("gender", ""))
        self.bed_var = StringVar(value=info.get("bed") or "None")
        self.checks_var = BooleanVar(value=info.get("checks", False))
        default_wakeup = info.get("wakeup_time") if info.get("wakeup_time") else "None"
        self.wakeup_var = StringVar(value=default_wakeup)
        self.return_time = info.get("return_time")
        self.property_vars = {
            k: BooleanVar(value=info.get("property", {}).get(k, False))
            for k in PROPERTY_KEYS
        }

        entry_width = 20
        row = 0
        Label(self, text="Name:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        Entry(self, textvariable=self.name_var, width=entry_width).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        Label(self, text="Gender:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        ttk.Combobox(
            self,
            textvariable=self.gender_var,
            values=[
                "Male",
                "Female",
                "Transgender Male",
                "Transgender Female",
            ],
            state="readonly",
            width=entry_width - 2,
        ).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        Label(self, text="Bed:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        bed_options = ["None"] + master.available_beds(exclude=info.get("bed"))
        ttk.Combobox(
            self,
            textvariable=self.bed_var,
            values=bed_options,
            state="readonly",
            width=entry_width - 2,
        ).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        check_frame = Frame(self)
        check_frame.grid(row=row, column=0, columnspan=2, sticky="w")
        Checkbutton(
            check_frame,
            text="15-minute checks",
            variable=self.checks_var,
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5, columnspan=2)
        Label(check_frame, text="Wakeup Time:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        times = ["None"] + [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
        ttk.Combobox(
            check_frame,
            textvariable=self.wakeup_var,
            values=times,
            state="readonly",
            width=entry_width - 2,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        row += 1

        Label(self, text="Approved Contacts:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        contacts_frame = Frame(self)
        contacts_frame.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        scroll = Scrollbar(contacts_frame, orient="vertical")
        self.contacts_text = Text(
            contacts_frame,
            height=4,
            width=20,
            wrap="word",
            yscrollcommand=scroll.set,
        )
        scroll.config(command=self.contacts_text.yview)
        self.contacts_text.pack(side="left", fill="both")
        scroll.pack(side="right", fill="y")
        self.contacts_text.insert("1.0", info.get("contacts", ""))
        row += 1

        Label(self, text="Property:").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        prop_frame = Frame(self)
        prop_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        for p in PROPERTY_KEYS:
            Checkbutton(prop_frame, text=p, variable=self.property_vars[p]).pack(anchor="w")
        row += 1

        if self.return_time is not None:
            Label(self, text="Est. Return:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
            times = [f"{h:02}:{m:02}" for h in range(24) for m in (0, 30)]
            self.return_var = StringVar(value=self.return_time)
            ttk.Combobox(
                self,
                values=times,
                textvariable=self.return_var,
                state="readonly",
                width=entry_width - 2,
            ).grid(row=row, column=1, padx=5, pady=5)
            row += 1

        button_frame = Frame(self)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        Button(
            button_frame,
            text="Close",
            command=self.destroy,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)
        Button(
            button_frame,
            text="Save",
            command=self._save,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="right", padx=BUTTON_PADX, pady=BUTTON_PADY)
        Button(
            button_frame,
            text="Discharge",
            fg=BUTTON_FG,
            bg=BUTTON_BG,
            command=self._discharge,
            padx=BUTTON_PADX,
            pady=BUTTON_PADY,
            font=BUTTON_FONT,
        ).pack(side="left", padx=BUTTON_PADX, pady=BUTTON_PADY)

        self.grab_set()

    def _save(self):
        bed_val = self.bed_var.get().strip()
        if bed_val == "None":
            bed_val = ""
        else:
            available = self.master.available_beds(exclude=self.info.get("bed"))
            if bed_val not in available and bed_val != self.info.get("bed"):
                messagebox.showwarning("Bed Unavailable", "Selected bed is already assigned")
                return
        new_data = {
            "name": self.name_var.get().strip(),
            "gender": self.gender_var.get().strip(),
            "bed": bed_val,
            "checks": self.checks_var.get(),
            "contacts": self.contacts_text.get("1.0", "end").strip(),
            "wakeup_time": None if self.wakeup_var.get() == "None" else self.wakeup_var.get(),
            "property": {k: var.get() for k, var in self.property_vars.items()},
        }
        if hasattr(self, "return_var"):
            new_data["return_time"] = self.return_var.get()
        self.master.update_client_info(self.info, new_data)
        self.destroy()

    def _discharge(self):
        confirm = messagebox.askyesno(
            "Discharge",
            "Has the client...\n"
            "1. Had their property returned?\n"
            "2. Spoken with the case manager?\n"
            "3. Spoken with medical?",
        )
        if confirm:
            self.master.discharge_client(self.info)
            self.destroy()
