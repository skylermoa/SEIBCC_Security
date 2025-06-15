from tkinter import Label
from ..constants import CLIENT_FONT

class DraggableLabel(Label):
    """A label that can be dragged with the mouse."""

    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text,
            bd=1,
            relief="raised",
            padx=5,
            pady=5,
            anchor="center",
            justify="center",
            font=CLIENT_FONT,
            **kwargs,
        )
        self.text = text
        self.bind("<ButtonPress-1>", self.on_start)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.bind("<Double-Button-1>", self.on_double_click)
        self._is_dragging = False
        self._mouse_down = False

    def on_start(self, event):
        self._is_dragging = False
        self._mouse_down = True
        self.lift()

    def on_drag(self, event):
        if not self._mouse_down:
            return
        if not self._is_dragging:
            self._is_dragging = True
            if hasattr(self.master, "start_drag"):
                self.master.start_drag(self)
        self.update_idletasks()
        new_x = event.x_root - self.master.winfo_rootx() - self.winfo_width() / 2
        new_y = event.y_root - self.master.winfo_rooty() - self.winfo_height() / 2
        self.place(in_=self.master, x=new_x, y=new_y)

    def on_drop(self, event):
        if self._is_dragging:
            self.master.on_drop(self, event)
        self._is_dragging = False
        self._mouse_down = False

    def on_double_click(self, event):
        if hasattr(self.master, "show_client_info"):
            self.master.show_client_info(self)
