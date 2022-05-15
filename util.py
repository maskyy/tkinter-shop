import tkinter.messagebox as _msg

__all__ = ["set_close_handler"]


def set_close_handler(win, func):
    win.protocol("WM_DELETE_WINDOW", func)


def show_error(text):
    _msg.showerror("Ошибка", text)
    return False
