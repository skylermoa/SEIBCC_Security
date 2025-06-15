from tkinter import TclError
from crisis_center.ui.app import CrisisCenterApp

if __name__ == "__main__":
    try:
        app = CrisisCenterApp()
        app.mainloop()
    except TclError as exc:
        print("Unable to start the GUI:", exc)