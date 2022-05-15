import tkinter as _tk
import tkinter.ttk as _ttk

import logo
import util
from db_sqlite import Database
from login import Login
from style import Entry
from tableview import TableView
from tabs import Tabs
from window import Window

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
        self.goods = TableView(main, self.db, "goods", goods_cols, self.on_good_select)
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

        self.code = Entry(master)
        self.code.grid(column=1, row=0, padx=5, pady=5)
        self.amount = Entry(master)
        self.amount.grid(column=1, row=1, padx=5, pady=5)

        self.add = _ttk.Button(master, text="Добавить", command=self.on_add_item)
        self.add.grid(column=0, row=2, columnspan=2, pady=5)

        self.code.bind("<Return>", lambda _: self.add.invoke())
        self.amount.bind("<Return>", lambda _: self.add.invoke())

    def create_confirm_window(self):
        self.confirm_window = _tk.Toplevel(self)
        self.confirm_return = Login(self.confirm_window, [("Подтвердить", lambda l, p: None)])
        self.confirm_return.pack()
        self.confirm_window.withdraw()

    def find_row(self, table, code):
        for row in table.get_children():
            if int(code) == table.item(row)["values"][0]:
                return row, table.item(row)["values"]
        return None, None

    def on_good_select(self, _, selected):
        self.code.delete(0, "end")
        self.amount.delete(0, "end")
        self.code.insert(0, selected["values"][0])
        self.amount.insert(0, 1)
        self.code.focus()

    def on_add_item(self):
        code, amount = self.code.get_strip(), self.amount.get_strip()
        if not code or len(code) != 13 or not code.isdigit():
            return util.show_error("Введите штрихкод из 13 цифр")

        row, values = self.find_row(self.goods, code)

        if not row:
            return util.show_error("Штрихкод не найден")
        if not amount.isdigit() or int(amount) <= 0:
            return util.show_error("Количество должно быть целым положительным числом")
        amount = int(amount)
        if amount > values[3]:
            return util.show_error("Нельзя продать больше товаров, чем есть в наличии")

        self.change_by_amount(code, -amount, row)
        self.add_to_check(code, amount, row)
        self.update_check_sum()

        self.code.delete(0, "end")
        self.amount.delete(0, "end")

    def change_by_amount(self, code, amount, row):
        values = self.goods.item(row)["values"]
        values[3] += amount
        self.goods.item(row, values=values)

    def add_to_check(self, code, amount, row):
        cost = amount * self.goods.item(row)["values"][4]
        self.check.insert("", "end", values=(code, amount, cost))

    def update_check_id(self):
        self.check_id = self.db.get_new_check_id()
        self.check_text.config(text="Чек №%d" % self.check_id)
    
    def update_check_sum(self):
        result = 0
        for row in self.check.get_children():
            result += self.check.item(row)["values"][2]
        self.check_sum.config(text="Сумма: %d" % result)


if __name__ == "__main__":
    root = _tk.Tk()
    root.withdraw()
    cashier = Cashier()
    util.set_close_handler(cashier, root.destroy)
    cashier.mainloop()
