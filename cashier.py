import tkinter as _tk
import tkinter.ttk as _ttk

import logo
from db_sqlite import Database
from login import Login
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
        main.pack(expand=True, fill="both", pady=20)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(1, weight=1)

        _ttk.Label(main, text="Товары").grid(column=0, row=0)
        self.check_text = _ttk.Label(main)
        self.check_text.grid(column=1, row=0)
        self.update_check_id()

        goods_cols = [
            "Штрихкод",
            "Наименование",
            "Производитель",
            "Количество",
            "Цена",
        ]
        self.goods = TableView(main, self.db, "goods", goods_cols)
        self.goods.grid(column=0, row=1, sticky="nsew", padx=20)
        self.goods.update_data()

        entries_frame = _ttk.Frame(main)
        self.create_entries(entries_frame)
        entries_frame.grid(column=0, row=2)

        self.check = TableView(main, columns=["Штрихкод", "Количество", "Стоимость"])
        self.check.grid(column=1, row=1, sticky="nsew", padx=20)

        check_frame = _ttk.Frame(main)
        check_frame.grid(column=1, row=2)

        self.check_sum = _ttk.Label(check_frame, text="Сумма: 0")
        self.check_sum.pack(pady=5)
        _ttk.Button(check_frame, text="Продать").pack(pady=5)
        _ttk.Button(check_frame, text="Вернуть").pack(pady=5)

        self.create_confirm_window()

    def create_entries(self, master):
        _ttk.Label(master, text="Штрихкод").grid(column=0, row=0, padx=5)
        _ttk.Label(master, text="Количество").grid(column=0, row=1, padx=5)

        self.item_code = Entry(master)
        self.item_code.grid(column=1, row=0, padx=5, pady=5)
        self.item_amount = Entry(master)
        self.item_amount.grid(column=1, row=1, padx=5, pady=5)

        self.add_item = _ttk.Button(master, text="Добавить")
        self.add_item.grid(column=0, row=2, columnspan=2, pady=5)

    def create_confirm_window(self):
        self.confirm_window = _tk.Toplevel(self)
        self.confirm_return = Login(self.confirm_window, [("Подтвердить", lambda l, p: None)])
        self.confirm_return.pack()
        self.confirm_window.withdraw()

    def update_check_id(self):
        self.check_id = self.db.get_new_check_id()
        self.check_text.config(text="Чек №%d" % self.check_id)


if __name__ == "__main__":
    root = _tk.Tk()
    root.withdraw()
    cashier = Cashier()
    cashier.protocol("WM_DELETE_WINDOW", root.destroy)
    cashier.mainloop()
