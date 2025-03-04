import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import datetime

# Set BASE_DIR to the folder where this script is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define game configurations. Folders will be under Launcher/<GameName>/...
games = {
    "CastleMiner Z": {
        "GAME_CACHE": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "GameCache"),
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Instances"),
        "EXE_NAME": "CastleMinerZ.exe",
        "VANILLA_VERSION": "Vanilla 1.9.8.0",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
        ]
    },
    "CastleMiner Warfare": {
        "GAME_CACHE": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "GameCache"),
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Instances"),
        "EXE_NAME": "CastleMinerWarfare.exe",
        "VANILLA_VERSION": "Vanilla 1.0.0",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Warfare",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Warfare"
        ]
    }
}


def ensure_game_folders(game):
    """Ensure that required folders exist for the given game."""
    for key in ["GAME_CACHE", "VERSIONS_DIR", "INSTANCES_DIR"]:
        folder = game[key]
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[INFO] Created folder: {folder}")


def cache_base_game_for_game(base_game_path, game):
    """Cache the base game for this game if not already cached."""
    cache_dir = game["GAME_CACHE"]
    if not os.path.exists(cache_dir) or not os.listdir(cache_dir):
        print(f"[INFO] Caching base game from: {base_game_path}")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        shutil.copytree(base_game_path, cache_dir)
    else:
        print("[INFO] Base game already cached.")


def find_install_location(game):
    """
    Try to auto-detect the install location for the game by checking its POSSIBLE_PATHS.
    """
    for path in game["POSSIBLE_PATHS"]:
        exe_path = os.path.join(path, game["EXE_NAME"])
        if os.path.exists(exe_path):
            return path
    return None


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


def centered_askyesno(parent, title, message):
    result = [None]
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("300x150")
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


class CacheDialog(tk.Toplevel):
    def __init__(self, master, game_name, game):
        super().__init__(master)
        self.game = game
        self.game_name = game_name
        self.title(f"Set Up {game_name}")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()  # Make the dialog modal.

        # Withdraw the window to hide it until centered.
        self.withdraw()
        self.update_idletasks()  # Ensure geometry is calculated.
        center_window(self, self.master.winfo_toplevel())
        self.deiconify()  # Now show the window

        self.attributes("-topmost", True)
        self.after_idle(lambda: self.attributes("-topmost", False))

        self.result = None

        tk.Label(self, text=f"Enter installation path for {game_name}:").pack(pady=10)
        self.entry = tk.Entry(self, width=50)
        self.entry.pack(pady=5)
        detected = find_install_location(game)
        if detected:
            self.entry.insert(0, detected)

        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack(pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        verify_btn = tk.Button(btn_frame, text="Verify", command=self.verify_path)
        verify_btn.grid(row=0, column=0, padx=5)
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.cancel)
        cancel_btn.grid(row=0, column=1, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.wait_window(self)

    def verify_path(self):
        path = self.entry.get().strip()
        exe_full_path = os.path.join(path, self.game["EXE_NAME"])
        if os.path.exists(path) and os.path.exists(exe_full_path):
            cache_base_game_for_game(path, self.game)
            self.result = path
            self.destroy()
        else:
            self.error_label.config(text="Invalid path or executable not found. Please try again.")

    def cancel(self):
        self.result = None
        self.destroy()


def overlay_version_files(instance_path, version, game):
    """
    Overlay version-specific files onto an instance folder.
    If version is the vanilla version, do nothing.
    Otherwise, overlay files from the Versions folder.
    """
    if version == game["VANILLA_VERSION"]:
        return
    version_path = os.path.join(game["VERSIONS_DIR"], version)
    if not os.path.exists(version_path):
        print(f"[ERROR] Version files for '{version}' not found in Versions folder!")
        return
    for root, _, files in os.walk(version_path):
        for file in files:
            relative_path = os.path.relpath(root, version_path)
            dest_path = os.path.join(instance_path, relative_path, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(os.path.join(root, file), dest_path)
            print(f"[INFO] Overlaying file: {dest_path}")


def get_instance_info(instance_path):
    """Read instance metadata from instance_info.json if available."""
    info_file = os.path.join(instance_path, "instance_info.json")
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"instance": os.path.basename(instance_path), "version": "", "last_played": ""}


def write_instance_info(instance_path, info):
    """Write instance metadata to instance_info.json."""
    info_file = os.path.join(instance_path, "instance_info.json")
    with open(info_file, "w") as f:
        json.dump(info, f)


def create_instance(instance_name, version, game):
    """
    Create a new instance with the given name and version.
    It is created by copying the GAME_CACHE and then overlaying version files.
    Also writes instance metadata.
    Returns the instance path on success; if the instance already exists, returns "exists";
    or returns an error message string if something went wrong.
    """
    instance_path = os.path.join(game["INSTANCES_DIR"], instance_name)
    if os.path.exists(instance_path):
        return "exists"
    try:
        print(f"[INFO] Creating new instance '{instance_name}' with version '{version}'...")
        shutil.copytree(game["GAME_CACHE"], instance_path)
        overlay_version_files(instance_path, version, game)
        info = {
            "instance": instance_name,
            "version": version,
            "last_played": ""
        }
        write_instance_info(instance_path, info)
        return instance_path
    except Exception as e:
        return str(e)


def launch_game(instance_path, game):
    """Launch the game from the given instance folder and update last played."""
    game_exe = os.path.join(instance_path, game["EXE_NAME"])
    app_id_path = os.path.join(instance_path, "steam_appid.txt")
    with open(app_id_path, "w") as f:
        f.write("253430")
    if os.path.exists(game_exe):
        print("[INFO] Launching game from instance...")
        env = os.environ.copy()
        env["PATH"] = instance_path + ";" + env["PATH"]
        env["PWD"] = instance_path
        subprocess.Popen(game_exe, cwd=instance_path, env=env)
        info = get_instance_info(instance_path)
        info["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_instance_info(instance_path, info)
    else:
        messagebox.showerror("Error", "Game executable not found in the instance folder.")


def open_instance_folder(instance_path):
    """Open the instance folder in Windows Explorer."""
    if os.path.exists(instance_path):
        subprocess.Popen(["explorer", instance_path])
    else:
        messagebox.showerror("Error", "Instance folder not found.")


def delete_instance(instance_path):
    """Delete the given instance folder after confirmation using a centered dialog."""
    if centered_askyesno(tk._default_root, "Confirm Delete", "Are you sure you want to delete this instance?"):
        try:
            shutil.rmtree(instance_path)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete instance: {e}")
    return False


def list_instances(game):
    """Return a list of instance folder names for the game."""
    if not os.path.exists(game["INSTANCES_DIR"]):
        os.makedirs(game["INSTANCES_DIR"])
    return [instance for instance in os.listdir(game["INSTANCES_DIR"])
            if os.path.isdir(os.path.join(game["INSTANCES_DIR"], instance))]


def get_version_options(game):
    """Return a list of available versions (vanilla plus folders in Versions)."""
    options = [game["VANILLA_VERSION"]]
    if os.path.exists(game["VERSIONS_DIR"]):
        for folder in os.listdir(game["VERSIONS_DIR"]):
            folder_path = os.path.join(game["VERSIONS_DIR"], folder)
            if os.path.isdir(folder_path):
                options.append(folder)
    return options


def create_new_version(game):
    """
    Open a modal dialog to create a new version for the game.
    Returns None if cancelled.
    """
    dialog = tk.Toplevel()
    dialog.title("Create New Version")
    dialog.geometry("300x150")
    dialog.transient()
    dialog.grab_set()
    center_window(dialog, app)

    tk.Label(dialog, text="Version Name:").pack(pady=5)
    version_var = tk.StringVar()
    version_var.set("")
    name_entry = tk.Entry(dialog, textvariable=version_var)
    name_entry.pack(pady=5)

    # Limit entry to 25 characters.
    def limit_version(*args):
        value = version_var.get()
        if len(value) > 25:
            version_var.set(value[:25])
    version_var.trace("w", limit_version)

    error_label = tk.Label(dialog, text="", fg="red")
    error_label.pack(pady=5)

    def on_create():
        version_name = version_var.get().strip()
        if not version_name:
            error_label.config(text="Version name cannot be empty.")
            return
        version_path = os.path.join(game["VERSIONS_DIR"], version_name)
        if os.path.exists(version_path):
            error_label.config(text="Version already exists.")
            return
        try:
            os.makedirs(version_path)
            dialog.destroy()
        except Exception as e:
            error_label.config(text=f"Error: {e}")

    tk.Button(dialog, text="Create Version", command=on_create).pack(pady=10)
    dialog.wait_window()
    return None  # Folder is created if successful.


# ----------------------------
# GUI Classes
# ----------------------------

class HomeTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        text = (
            "Welcome to CMLauncher!\n\n"
            "This launcher allows you to manage multiple instances of your games and apply "
            "different versions/modifications.\n\n"
            "Use the tabs above to manage each game. For each game, you must first cache the base game. "
            "If the base game is not cached, the game tab will be greyed out. Click on the overlay to set up the game."
        )
        label = tk.Label(self, text=text, justify=tk.LEFT)
        label.pack(padx=20, pady=20, anchor="w")


class GameTab(tk.Frame):
    def __init__(self, master, game_name, game):
        super().__init__(master)
        self.game_name = game_name
        self.game = game
        ensure_game_folders(self.game)
        self.overlay = None  # To hold the setup overlay
        self.sort_column = "instance"  # Default sort column
        self.sort_reverse = False
        self.create_widgets()
        self.populate_instances()
        self.check_base_game()

    def create_widgets(self):
        header = tk.Label(self, text=self.game_name, font=("Arial", 16))
        header.pack(pady=5)

        # Button frame with three groups: left (Versions, New Instance), center (Play), right (Open Folder, Delete)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)

        left_frame = tk.Frame(btn_frame)
        left_frame.pack(side=tk.LEFT, padx=5)
        self.versions_btn = tk.Button(left_frame, text="Versions", command=self.manage_versions_dialog)
        self.versions_btn.pack(side=tk.LEFT, padx=2)
        self.new_instance_btn = tk.Button(left_frame, text="New Instance", command=self.new_instance_dialog)
        self.new_instance_btn.pack(side=tk.LEFT, padx=2)

        center_frame = tk.Frame(btn_frame)
        center_frame.pack(side=tk.LEFT, expand=True)
        self.play_btn = tk.Button(center_frame, text="   Play   ", command=self.start_instance)
        self.play_btn.pack()

        right_frame = tk.Frame(btn_frame)
        right_frame.pack(side=tk.RIGHT, padx=5)
        self.open_btn = tk.Button(right_frame, text="Open Folder", command=self.open_instance)
        self.open_btn.pack(side=tk.LEFT, padx=2)
        self.delete_btn = tk.Button(right_frame, text="Delete", command=self.delete_instance)
        self.delete_btn.pack(side=tk.LEFT, padx=2)

        # Treeview for instances with sortable headers
        columns = ("instance", "version", "last_played")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("instance", text="Instance", command=lambda: self.sort_by("instance"))
        self.tree.heading("version", text="Version", command=lambda: self.sort_by("version"))
        self.tree.heading("last_played", text="Last Played", command=lambda: self.sort_by("last_played"))
        self.tree.column("instance", anchor="w", width=150)
        self.tree.column("version", anchor="w", width=100)
        self.tree.column("last_played", anchor="w", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_instance_select)

    def check_base_game(self):
        cache_dir = self.game["GAME_CACHE"]
        if not os.path.exists(cache_dir) or not os.listdir(cache_dir):
            self.show_setup_overlay()
        else:
            self.hide_setup_overlay()

    def show_setup_overlay(self):
        if self.overlay is None:
            self.overlay = tk.Frame(self, bg="light grey")
            self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            msg = tk.Label(self.overlay, text="Base game not cached!\nClick the button below to set up.",
                           fg="red", bg="light grey", font=("Arial", 14))
            msg.pack(pady=20)
            setup_btn = tk.Button(self.overlay, text="Set Up Game", command=self.open_cache_dialog)
            setup_btn.pack()
        self.set_action_buttons_state(False)

    def hide_setup_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def open_cache_dialog(self):
        dlg = CacheDialog(self, self.game_name, self.game)
        self.check_base_game()
        self.populate_instances()

    def new_instance_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Instance")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)  # Center the dialog relative to the main window

        tk.Label(dialog, text="Instance Name:").pack(pady=5)
        instance_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=instance_var)
        name_entry.pack(pady=5)

        error_label = tk.Label(dialog, text="", fg="red")
        error_label.pack(pady=5)

        tk.Label(dialog, text="Version:").pack(pady=5)
        version_options = get_version_options(self.game)
        selected_version = tk.StringVar(dialog)
        selected_version.set(version_options[0])
        version_menu = tk.OptionMenu(dialog, selected_version, *version_options)
        version_menu.pack(pady=5)

        def on_create():
            instance_name = instance_var.get().strip()
            if not instance_name:
                error_label.config(text="Instance name cannot be empty.")
                return
            if len(instance_name) > 25:
                error_label.config(text="Instance name cannot exceed 25 characters.")
                return
            if os.path.exists(os.path.join(self.game["INSTANCES_DIR"], instance_name)):
                error_label.config(text="An instance with that name already exists.")
                return
            version = selected_version.get()
            result = create_instance(instance_name, version, self.game)
            if result is None or result == "exists":
                error_label.config(text="Failed to create instance.")
            else:
                self.populate_instances()
                dialog.destroy()

        tk.Button(dialog, text="Create Instance", command=on_create).pack(pady=10)
        dialog.wait_window()

    def new_version_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Version")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)  # Center the dialog relative to the main window

        tk.Label(dialog, text="Version Name:").pack(pady=5)
        version_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=version_var)
        name_entry.pack(pady=5)

        error_label = tk.Label(dialog, text="", fg="red")
        error_label.pack(pady=5)

        def on_create():
            version_name = version_var.get().strip()
            if not version_name:
                error_label.config(text="Version name cannot be empty.")
                return
            if len(version_name) > 25:
                error_label.config(text="Version name cannot exceed 25 characters.")
                return
            version_path = os.path.join(self.game["VERSIONS_DIR"], version_name)
            if os.path.exists(version_path):
                error_label.config(text="Version already exists.")
                return
            try:
                os.makedirs(version_path)
                dialog.destroy()
            except Exception as e:
                error_label.config(text=f"Error: {e}")

        tk.Button(dialog, text="Create Version", command=on_create).pack(pady=10)
        dialog.wait_window()

    def populate_instances(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for instance in list_instances(self.game):
            instance_path = os.path.join(self.game["INSTANCES_DIR"], instance)
            info_file = os.path.join(instance_path, "instance_info.json")
            if os.path.exists(info_file):
                try:
                    with open(info_file, "r") as f:
                        info = json.load(f)
                except Exception:
                    info = {"instance": instance, "version": "", "last_played": ""}
            else:
                info = {"instance": instance, "version": "", "last_played": ""}
            self.tree.insert("", "end", values=(info.get("instance", instance),
                                                 info.get("version", ""),
                                                 info.get("last_played", "")))
        self.sort_tree(self.sort_column, self.sort_reverse)
        self.set_action_buttons_state(False)

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.sort_tree(self.sort_column, self.sort_reverse)

    def sort_tree(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        if col == "last_played":
            def conv(x):
                try:
                    return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    return datetime.datetime.min
            l = [(conv(val), k) for (val, k) in l]
        l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, "", index)

    def on_instance_select(self, event):
        if self.tree.selection():
            self.set_action_buttons_state(True)
        else:
            self.set_action_buttons_state(False)

    def set_action_buttons_state(self, state):
        st = tk.NORMAL if state else tk.DISABLED
        self.play_btn.config(state=st)
        self.open_btn.config(state=st)
        self.delete_btn.config(state=st)

    def get_selected_instance_path(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            instance_name = item["values"][0]
            return os.path.join(self.game["INSTANCES_DIR"], instance_name)
        return None

    def start_instance(self):
        path = self.get_selected_instance_path()
        if path:
            launch_game(path, self.game)
            info_file = os.path.join(path, "instance_info.json")
            info = {}
            if os.path.exists(info_file):
                try:
                    with open(info_file, "r") as f:
                        info = json.load(f)
                except Exception:
                    info = {}
            info["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            write_instance_info(path, info)
            self.populate_instances()

    def open_instance(self):
        path = self.get_selected_instance_path()
        if path:
            open_instance_folder(path)

    def delete_instance(self):
        path = self.get_selected_instance_path()
        if path and delete_instance(path):
            self.populate_instances()

    def manage_versions_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Manage Versions")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)  # Center the dialog relative to the main app window

        # Listbox to display all versions
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            listbox.delete(0, tk.END)
            versions = get_version_options(self.game)
            for v in versions:
                listbox.insert(tk.END, v)

        refresh_list()

        # Create button frame
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)

        def create_new():
            self.new_version_dialog()
            refresh_list()

        def delete_selected():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            version_name = listbox.get(sel[0])
            if version_name == self.game["VANILLA_VERSION"]:
                custom_error(dialog, "Error", "Cannot delete the vanilla version.")
                return
            version_path = os.path.join(self.game["VERSIONS_DIR"], version_name)
            if centered_askyesno(self.winfo_toplevel(), "Confirm Delete", f"Delete version '{version_name}'?"):
                try:
                    shutil.rmtree(version_path)
                    refresh_list()
                except Exception as e:
                    custom_error(dialog, "Error", f"Failed to delete version: {e}")

        def open_folder():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            version_name = listbox.get(sel[0])
            if version_name == self.game["VANILLA_VERSION"]:
                folder = self.game["GAME_CACHE"]
            else:
                folder = os.path.join(self.game["VERSIONS_DIR"], version_name)
            if os.path.exists(folder):
                subprocess.Popen(["explorer", folder])
            else:
                custom_error(dialog, "Error", "Folder not found.")

        # Create buttons and store Delete button for later state updates.
        tk.Button(btn_frame, text="Create New", command=create_new).pack(side=tk.LEFT, padx=5)
        btn_delete = tk.Button(btn_frame, text="Delete Selected", command=delete_selected)
        btn_delete.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Open Folder", command=open_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Bind selection change to enable/disable Delete button.
        def on_select(event):
            sel = listbox.curselection()
            if sel:
                version_name = listbox.get(sel[0])
                if version_name == self.game["VANILLA_VERSION"]:
                    btn_delete.config(state=tk.DISABLED)
                else:
                    btn_delete.config(state=tk.NORMAL)
            else:
                btn_delete.config(state=tk.DISABLED)

        listbox.bind("<<ListboxSelect>>", on_select)

        dialog.wait_window()


class LauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMLauncher")
        self.geometry("600x500")
        self.create_tabs()

    def create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        home_tab = HomeTab(notebook)
        notebook.add(home_tab, text="Home")

        for game_name, game in games.items():
            game_tab = GameTab(notebook, game_name, game)
            notebook.add(game_tab, text=game_name)


def initial_setup():
    """Perform initial setup: create required folders for each game and try auto-detect caching if possible."""
    for game in games.values():
        ensure_game_folders(game)
    for game_name, game in games.items():
        if not os.path.exists(game["GAME_CACHE"]) or not os.listdir(game["GAME_CACHE"]):
            temp = tk.Tk()
            temp.withdraw()
            detected = find_install_location(game)
            if detected:
                if messagebox.askyesno("Confirm Install Location",
                                       f"Detected {game_name} installation at:\n{detected}\nCache base game from here?"):
                    cache_base_game_for_game(detected, game)
            temp.destroy()


if __name__ == "__main__":
    initial_setup()
    app = LauncherGUI()
    app.mainloop()
