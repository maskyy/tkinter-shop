import tkinter as _tk
import tkinter.ttk as _ttk

import logo
from db_sqlite import Database
from window import Window
from tabs import Tabs
from tableview import TableView
from style import Entry

__all__ = ["Cashier"]


class Cashier(Window):
    def __init__(self):
        super().__init__("Касса")
        self.db = Database()
        self.create_widgets()

    def create_widgets(self):
        logo.get_label(self).pack()
        main = _ttk.Frame(self)
        main.pack(expand=True, fill="both", padx=20, pady=20)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        _ttk.Label(main, text="Товары").grid(column=0, row=0)
        goods_cols = [
            "Штрихкод",
            "Наименование",
            "Производитель",
            "Количество",
            "Цена",
        ]
        self.goods = TableView(main, self.db, "goods", goods_cols)
        self.goods.grid(column=0, row=1, sticky="nsew")



if __name__ == "__main__":
    root = _tk.Tk()
    root.withdraw()
    cashier = Cashier()
    cashier.protocol("WM_DELETE_WINDOW", root.destroy)
    cashier.mainloop()
