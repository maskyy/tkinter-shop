import sqlite3 as _sql

__all__ = ["Database"]

_default_name = "files/goods.sqlite3"

_init_script = """
PRAGMA encoding = 'UTF-8';
PRAGMA foreign_keys = 1;

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS goods (
    barcode TEXT PRIMARY KEY CHECK(length(barcode) == 13),
    name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0 CHECK(amount >= 0),
    price INTEGER NOT NULL DEFAULT 0 CHECK(price >= 0)
) STRICT;

CREATE TABLE IF NOT EXISTS checks (
    id INTEGER PRIMARY KEY,
    sum INTEGER NOT NULL DEFAULT 0 CHECK(sum >= 0)
) STRICT;

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    check_id INTEGER,
    barcode TEXT,
    amount INTEGER NOT NULL DEFAULT 0 CHECK(amount > 0),
    cost INTEGER NOT NULL DEFAULT 0 CHECK(cost >= 0),
    FOREIGN KEY(check_id) REFERENCES checks(id) ON DELETE CASCADE,
    FOREIGN KEY(barcode) REFERENCES goods(barcode) ON UPDATE CASCADE 
) STRICT;
"""

_exit_script = """
PRAGMA analysis_limit = 1000;
PRAGMA optimize;
"""


def _check_args(length, *args):
    if length != len(*args):
        raise Exception("Wrong number of arguments")


class Database:
    def __init__(self, filename=_default_name):
        self.con = _sql.connect(filename)
        self.cur = self.con.cursor()
        self.cur.executescript(_init_script)

    def __del__(self):
        self.cur.executescript(_exit_script)
        self.cur.close()
        self.save()
        self.con.close()

    def save(self):
        self.con.commit()

    def get_table(self, name):
        return self.cur.execute("SELECT * FROM %s" % name).fetchall()

    def execute(self, *args):
        return self.cur.execute(*args)

    def get_columns(self, table):
        self.cur.execute("SELECT name FROM PRAGMA_TABLE_INFO('%s')" % table)
        return [name[0] for name in self.cur.fetchall()]

    def add_product(self, *args):
        _check_args(5, args)
        self.cur.execute("INSERT INTO goods VALUES (?, ?, ?, ?, ?)", args)

    def update_product(self, barcode, *args):
        _check_args(4, args)
        self.cur.execute(
            "UPDATE goods SET name = ?, manufacturer = ?, amount = ?, price = ? WHERE barcode = ?",
            args + (barcode,),
        )

    def get_new_check_id(self):
        result = self.cur.execute("SELECT MAX(id)+1 FROM checks").fetchone()[0]
        return 1 if not result else result

    def add_check(self, id_):
        self.cur.execute("INSERT INTO checks VALUES (?, 0)", (id_,))

    def sell_product(self, check_id, barcode, amount, cost):
        count = self.cur.execute(
            "SELECT amount FROM goods WHERE barcode = ?", (barcode,)
        ).fetchone()[0]
        new_amount = count - amount
        self.cur.execute(
            "UPDATE goods SET amount = ? WHERE barcode = ?", (new_amount, barcode)
        )

        self.cur.execute(
            "INSERT INTO sales VALUES (NULL, ?, ?, ?, ?)",
            (check_id, barcode, amount, cost),
        )
        self.cur.execute(
            "UPDATE checks SET sum = sum + ? WHERE id = ?", (cost, check_id)
        )
