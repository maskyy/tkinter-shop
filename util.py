__all__ = ["set_close_handler"]


def set_close_handler(win, func):
    win.protocol("WM_DELETE_WINDOW", func)
