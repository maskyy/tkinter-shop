import enum as _enum
import tkinter as _tk
import tkinter.messagebox as _msg
import tkinter.ttk as _ttk

import logo
import util
from db_sqlite import Database
from style import Entry
from tableview import TableView
from tabs import Tabs
from window import Window

__all__ = ["Admin"]


class DeliveryActions(_enum.Enum):
    INSERT = "Вставить"
    ADD = "Добавить"
    UPDATE = "Обновить"


class Admin(Window):
    def __init__(self):
        super().__init__("Панель администратора")
        self.db = Database()
        self.goods_cols = [
            "Штрихкод",
            "Наименование",
            "Производитель",
            "Количество",
            "Цена",
        ]

        self.create_widgets()

    def create_widgets(self):
        logo.get_label(self).pack()
        tabs = Tabs(self)
        tabs.populate(
            {
                self.create_goods: "Товары",
                self.create_delivery: "Поставка",
                self.create_sales: "Продажи",
            }
        )

    def create_goods(self, master):
        frame = _ttk.Frame(master)
        self.goods = TableView(frame, self.db, "goods", self.goods_cols)
        self.goods.update_data()
        self.goods.pack(expand=True, fill="both", padx=20, pady=20)
        _ttk.Button(frame, text="Обновить", command=self.goods.update_data).pack(pady=15)
        return frame

    def create_delivery(self, master):
        frame = _ttk.Frame(master)
        self.delivery = TableView(frame, columns=self.goods_cols + ["Действие"])
        self.delivery.grid(column=0, row=0, sticky="nsew", padx=20, pady=20)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        subframe = _ttk.Frame(frame)
        subframe.grid(column=1, row=0, sticky="n", padx=10, pady=20)
        self.product_info = self.add_product_entries(subframe)
        _ttk.Button(subframe, text="Добавить", command=self.add_product).pack(pady=2)
        _ttk.Button(
            subframe, text="Завершить поставку", command=self.make_delivery
        ).pack(pady=40)

        return frame

    def add_product_entries(self, master):
        entries = []
        for i in range(len(self.goods_cols)):
            name = self.goods_cols[i]
            _ttk.Label(master, text=name).pack(pady=2)
            e = Entry(master)
            e.pack(pady=2)
            entries.append(e)
        return entries

    def validate_add_data(self, barcode, amount):
        if not barcode or len(barcode) != 13 or not barcode.isdigit():
            return util.show_error("Введите штрихкод из 13 цифр")

        if not amount or (not amount.isdigit() or int(amount) < 0):
            return util.show_error("Количество должно быть целым неотрицательным числом")

        return True

    def validate_other_data(self, name, manufacturer, price):
        if not name:
            return util.show_error("Наименование товара не должно быть пустым")

        if not manufacturer:
            return util.show_error("Производитель не должен быть пустым")

        if not price or (not price.isdigit() or int(price) < 0):
            return util.show_error("Цена должна быть целым неотрицательным числом")

        return True

    def product_exists(self, barcode):
        for row in self.goods.get_children():
            if str(self.goods.item(row)["values"][0]) == barcode:
                return True

        for row in self.delivery.get_children():
            if str(self.delivery.item(row)["values"][0]) == barcode:
                return True

        return False

    def add_product(self):
        info = [e.get_strip() for e in self.product_info]
        barcode, name, manufacturer, amount, price = info
        action = DeliveryActions.INSERT

        if not self.validate_add_data(barcode, amount):
            return
        if self.product_exists(barcode):
            result = _msg.askyesno(
                "",
                "Да - добавить количество к существующему товару, нет - обновить его данные",
            )
            if result:
                action = DeliveryActions.ADD
            else:
                action = DeliveryActions.UPDATE

        if action != DeliveryActions.ADD and not self.validate_other_data(
            name, manufacturer, price
        ):
            return

        self.delivery.insert("", "end", values=info + [action.value])
        [e.delete(0, "end") for e in self.product_info]

    def make_delivery(self):
        for row in self.delivery.get_children():
            row = self.delivery.item(row)["values"]
            if row[-1] == DeliveryActions.INSERT.value:
                self.db.add_product(*row[:-1])
            elif row[-1] == DeliveryActions.ADD.value:
                self.db.change_by_amount(row[0], row[3])
            else:
                kwargs = dict(
                    zip(["name", "manufacturer", "amount", "price"], row[1:-1])
                )
                self.db.update_product(row[0], **kwargs)

        self.delivery.clear()
        self.goods.update_data()

    def create_sales(self, master):
        frame = _ttk.Frame(master)
        column_names = ["ID", "ID чека", "Штрихкод", "Количество", "Стоимость"]
        display_columns = [n for n in column_names if n != "ID"]

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=2)

        self.checks = TableView(frame, self.db, "checks", ["ID чека", "Сумма"])
        self.checks.update_data()
        self.checks.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        self._check_sum = _ttk.Label(frame)
        self.update_check_sum()
        self._check_sum.grid(column=0, row=1)

        self.sales = TableView(frame, self.db, "sales", column_names)
        self.sales.config(displaycolumns=display_columns)
        self.sales.update_data()
        self.sales.grid(column=1, row=0, sticky="ew", padx=5, pady=5)

        return frame

    def update_check_sum(self):
        result = 0
        for row in self.checks.get_children():
            result += self.checks.item(row)["values"][1]
        self._check_sum.config(text="Выручка: %d" % result)


if __name__ == "__main__":
    root = _tk.Tk()
    root.withdraw()
    admin = Admin()
    util.set_close_handler(admin, root.destroy)
    admin.mainloop()
