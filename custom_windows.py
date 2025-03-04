import tkinter as tk

def center_window(window, parent):
    window.update_idletasks()
    parent.update_idletasks()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = parent_x + (parent_width - window_width) // 2
    y = parent_y + (parent_height - window_height) // 2
    window.geometry(f"+{x}+{y}")


def custom_validated_askstring(parent, title, prompt, validation_func):
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("300x180")
    dlg.transient(parent)
    dlg.grab_set()
    center_window(dlg, parent)
    tk.Label(dlg, text=prompt, wraplength=280, justify=tk.LEFT).pack(pady=5)
    entry_var = tk.StringVar()
    entry = tk.Entry(dlg, textvariable=entry_var)
    entry.pack(pady=5)
    error_label = tk.Label(dlg, text="", fg="red")
    error_label.pack(pady=5)
    result = [None]
    def on_ok():
        value = entry_var.get().strip()
        error = validation_func(value)
        if error:
            error_label.config(text=error)
        else:
            result[0] = value
            dlg.destroy()
    tk.Button(dlg, text="OK", command=on_ok, width=10).pack(pady=5)
    dlg.wait_window()
    return result[0]


def custom_askstring(parent, title, prompt):
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("300x150")
    dlg.transient(parent)
    dlg.grab_set()
    center_window(dlg, parent)
    tk.Label(dlg, text=prompt, wraplength=280, justify=tk.LEFT).pack(pady=10)
    entry_var = tk.StringVar()
    tk.Entry(dlg, textvariable=entry_var).pack(pady=5)
    result = [None]
    def on_ok():
        result[0] = entry_var.get()
        dlg.destroy()
    tk.Button(dlg, text="OK", command=on_ok, width=10).pack(pady=10)
    dlg.wait_window()
    return result[0]


def custom_info(parent, title, message):
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("300x150")
    dlg.transient(parent)
    dlg.grab_set()
    center_window(dlg, parent)
    tk.Label(dlg, text=message, wraplength=280, justify=tk.LEFT).pack(pady=20)
    tk.Button(dlg, text="OK", command=dlg.destroy, width=10).pack(pady=10)
    dlg.wait_window()


def custom_error(parent, title, message):
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("300x150")
    dlg.transient(parent)
    dlg.grab_set()
    center_window(dlg, parent)
    tk.Label(dlg, text=message, wraplength=280, justify=tk.LEFT, fg="red").pack(pady=20)
    tk.Button(dlg, text="OK", command=dlg.destroy, width=10).pack(pady=10)
    dlg.wait_window()


def centered_askyesno(parent, title, message, height=150, width=300):
    result = [None]
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.transient(parent)
    dialog.grab_set()
    center_window(dialog, parent)
    tk.Label(dialog, text=message, wraplength=280, justify=tk.LEFT).pack(pady=20)
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    def on_yes():
        result[0] = True
        dialog.destroy()
    def on_no():
        result[0] = False
        dialog.destroy()
    tk.Button(button_frame, text="Yes", command=on_yes, width=10).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="No", command=on_no, width=10).pack(side=tk.LEFT, padx=10)
    dialog.wait_window()
    return result[0]