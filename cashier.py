import tkinter as tk

import logo
from db_sqlite import Database
from window import Window

__all__ = ["Cashier"]


class Cashier(Window):
    def __init__(self):
        super().__init__("Касса")
        self.db = Database()
        self.create_widgets()

    def create_widgets(self):
        logo.get_label(self).pack()


if __name__ == "__main__":
    root = _tk.Tk()
    root.withdraw()
    cashier = Cashier()
    cashier.protocol("WM_DELETE_WINDOW", root.destroy)
    cashier.mainloop()
