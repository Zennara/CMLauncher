import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, simpledialog
import json
import datetime

# Set BASE_DIR to the folder where this script is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define game configurations. Folders will be under Launcher/<GameName>/...
games = {
    "CastleMiner Z": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Instances"),
        "EXE_NAME": "CastleMinerZ.exe",
        "VANILLA_VERSION": "Steam Version",  # Base game version name.
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
        ]
    },
    "CastleMiner Warfare": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Instances"),
        "EXE_NAME": "CastleMinerWarfare.exe",
        "VANILLA_VERSION": "Steam Version",  # Base game version name.
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Warfare",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Warfare"
        ]
    }
}


def ensure_game_folders(game):
    """Ensure that required folders exist for the given game."""
    for key in ["VERSIONS_DIR", "INSTANCES_DIR"]:
        folder = game[key]
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[INFO] Created folder: {folder}")


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


# --- Global Instance Info --- #
def get_global_instance_info(game):
    """Retrieve last played and other info for the Global Instance."""
    info_file = os.path.join(game["INSTANCES_DIR"], "Global_Instance_Info.json")
    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"instance": "Global Instance", "version": game["VANILLA_VERSION"], "last_played": ""}
    else:
        return {"instance": "Global Instance", "version": game["VANILLA_VERSION"], "last_played": ""}


def write_global_instance_info(game, info):
    """Write Global Instance metadata to a file."""
    info_file = os.path.join(game["INSTANCES_DIR"], "Global_Instance_Info.json")
    with open(info_file, "w") as f:
        json.dump(info, f)


def create_instance(instance_name, version, game, force_copy=False):
    """
    Create a new instance with the given name and version.
    For modded instances, this copies all files from the version folder.
    Note: When creating an instance with the vanilla (Steam) version,
    if force_copy is False, the function will not copy (as that is reserved for the Global Instance).
    If force_copy is True, the installed game files (detected via find_install_location)
    are copied.
    """
    instance_path = os.path.join(game["INSTANCES_DIR"], instance_name)
    if os.path.exists(instance_path):
        return "exists"
    try:
        print(f"[INFO] Creating new instance '{instance_name}' with version '{version}'...")
        if version == game["VANILLA_VERSION"]:
            if not force_copy:
                return "Global instance is not copied."
            else:
                source_path = find_install_location(game)
                if not source_path:
                    return "Installation for vanilla version not found!"
        else:
            source_path = os.path.join(game["VERSIONS_DIR"], version)
            if not os.path.exists(source_path):
                return f"Version folder for '{version}' not found!"
        shutil.copytree(source_path, instance_path)
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
    """Launch the game from the given instance folder (or base directory) and update last played."""
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
    else:
        custom_error(tk._default_root, "Error", "Game executable not found in the instance folder.")


def open_instance_folder(instance_path):
    """Open the instance folder in Windows Explorer."""
    if os.path.exists(instance_path):
        subprocess.Popen(["explorer", instance_path])
    else:
        custom_error(tk._default_root, "Error", "Folder not found.")


def delete_instance(instance_path):
    """Delete the given instance folder after confirmation using a centered dialog."""
    if centered_askyesno(tk._default_root, "Confirm Delete", "Are you sure you wish to delete this instance?"):
        try:
            shutil.rmtree(instance_path)
            return True
        except Exception as e:
            custom_error(tk._default_root, "Error", f"Failed to delete instance: {e}")
    return False


def list_instances(game):
    """Return a list of instance folder names for the game (excluding the Global Instance)."""
    if not os.path.exists(game["INSTANCES_DIR"]):
        os.makedirs(game["INSTANCES_DIR"])
    return [instance for instance in os.listdir(game["INSTANCES_DIR"])
            if os.path.isdir(os.path.join(game["INSTANCES_DIR"], instance)) and instance != "Global Instance"]


def get_version_options(game):
    """Return a list of available versions (vanilla plus folders in Versions)."""
    options = [game["VANILLA_VERSION"]]
    if os.path.exists(game["VERSIONS_DIR"]):
        for folder in os.listdir(game["VERSIONS_DIR"]):
            folder_path = os.path.join(game["VERSIONS_DIR"], folder)
            if os.path.isdir(folder_path):
                options.append(folder)
    return options


def new_version_dialog(game, parent):
    """
    Open a modal dialog to create a new version for the game.
    Returns None if cancelled.
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Create New Version")
    dialog.geometry("300x150")
    dialog.transient(parent)
    dialog.grab_set()
    center_window(dialog, parent)

    tk.Label(dialog, text="Version Name:").pack(pady=5)
    version_var = tk.StringVar()
    name_entry = tk.Entry(dialog, textvariable=version_var)
    name_entry.pack(pady=5)

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
    return None


def get_product_version(exe_path):
    try:
        import win32api
        info = win32api.GetFileVersionInfo(exe_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{(ms >> 16) & 0xFFFF}.{ms & 0xFFFF}.{(ls >> 16) & 0xFFFF}.{ls & 0xFFFF}"
    except Exception:
        return "Unknown"


# --- Helper functions for cloning ---
def clone_instance(instance_name, game):
    """Clone an instance (including Global Instance) with a new name."""
    if instance_name == "Global Instance":
        source = find_install_location(game)
        if not source:
            custom_error(tk._default_root, "Error", "Global Instance source not found.")
            return
    else:
        source = os.path.join(game["INSTANCES_DIR"], instance_name)
    new_name = custom_askstring(tk._default_root, "Clone Instance", "Enter new instance name:")
    if not new_name:
        return
    new_path = os.path.join(game["INSTANCES_DIR"], new_name)
    if os.path.exists(new_path):
        custom_error(tk._default_root, "Error", "An instance with that name already exists.")
        return
    try:
        shutil.copytree(source, new_path)
        # Update the cloned instance's metadata
        info = get_instance_info(new_path)
        info["instance"] = new_name
        write_instance_info(new_path, info)
        custom_info(tk._default_root, "Clone", f"Instance cloned as '{new_name}'.")
    except Exception as e:
        custom_error(tk._default_root, "Error", f"Failed to clone instance: {e}")


def clone_version(version_name, game):
    """Clone a version folder with a new name."""
    if version_name == game["VANILLA_VERSION"]:
        custom_error(tk._default_root, "Error", "Cannot clone the vanilla version.")
        return
    source = os.path.join(game["VERSIONS_DIR"], version_name)
    new_name = custom_askstring(tk._default_root, "Clone Version", "Enter new version name:")
    if not new_name:
        return
    new_path = os.path.join(game["VERSIONS_DIR"], new_name)
    if os.path.exists(new_path):
        custom_error(tk._default_root, "Error", "A version with that name already exists.")
        return
    try:
        shutil.copytree(source, new_path)
        custom_info(tk._default_root,"Clone", f"Version cloned as '{new_name}'.")
    except Exception as e:
        custom_error(tk._default_root, "Error", f"Failed to clone version: {e}")


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
            "Use the tabs above to manage each game."
        )
        label = tk.Label(self, text=text, justify=tk.LEFT)
        label.pack(padx=20, pady=20, anchor="w")


class GameTab(tk.Frame):
    def __init__(self, master, game_name, game):
        super().__init__(master)
        self.game_name = game_name
        self.game = game
        ensure_game_folders(self.game)
        self.sort_column = "instance"
        self.sort_reverse = False

        if find_install_location(self.game) is None:
            self.load_no_install_ui()
        else:
            self.create_widgets()
            self.populate_instances()

    def load_no_install_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        label = tk.Label(self, text=f"Installation for {self.game_name} not detected.")
        label.pack(pady=20)
        btn = tk.Button(self, text="Set Steam Installation Path", command=self.set_install_path)
        btn.pack(pady=10)

    def set_install_path(self):
        path = custom_askstring(tk._default_root, "Set Installation Path", f"Enter the Steam installation path for {self.game_name}:")
        if path:
            exe_path = os.path.join(path, self.game["EXE_NAME"])
            if os.path.exists(exe_path):
                self.game["POSSIBLE_PATHS"].insert(0, path)
                for widget in self.winfo_children():
                    widget.destroy()
                self.create_widgets()
                self.populate_instances()
            else:
                custom_error(tk._default_root, "Error", f"Executable not found at provided path:\n{exe_path}")

    def create_widgets(self):
        header = tk.Label(self, text=self.game_name, font=("Arial", 16))
        header.pack(pady=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=5)

        left_frame = tk.Frame(btn_frame)
        left_frame.pack(side=tk.LEFT, padx=5)
        self.versions_btn = tk.Button(left_frame, text="Versions", command=self.manage_versions_dialog)
        self.versions_btn.pack(side=tk.LEFT, padx=2)
        self.instances_btn = tk.Button(left_frame, text="Instances", command=self.manage_instances_dialog)
        self.instances_btn.pack(side=tk.LEFT, padx=2)

        center_frame = tk.Frame(btn_frame)
        center_frame.pack(side=tk.LEFT, expand=True)
        self.play_btn = tk.Button(center_frame, text="   Play   ", command=self.start_instance, state=tk.DISABLED)
        self.play_btn.pack()

        right_frame = tk.Frame(btn_frame)
        right_frame.pack(side=tk.RIGHT, padx=5)
        self.open_btn = tk.Button(right_frame, text="Open Folder", command=self.open_instance)
        self.open_btn.pack(side=tk.LEFT, padx=2)

        self.tree = ttk.Treeview(self, columns=("instance", "version", "last_played"), show="headings")
        self.tree.heading("instance", text="Instance", command=lambda: self.sort_by("instance"))
        self.tree.heading("version", text="Version", command=lambda: self.sort_by("version"))
        self.tree.heading("last_played", text="Last Played", command=lambda: self.sort_by("last_played"))
        self.tree.column("instance", anchor="w", width=150)
        self.tree.column("version", anchor="w", width=100)
        self.tree.column("last_played", anchor="w", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_instance_select)
        self.tree.bind("<Button-3>", self.show_main_context)

    def show_main_context(self, event):
        rowid = self.tree.identify_row(event.y)
        if rowid:
            self.tree.selection_set(rowid)
            item = self.tree.item(rowid)
            instance_name = item["values"][0]
            menu = tk.Menu(self, tearoff=0)
            # Delete is disabled for Global Instance.
            if instance_name == "Global Instance":
                menu.add_command(label="Delete", state="disabled")
            else:
                menu.add_command(label="Delete", command=self.delete_selected_main)
            # Always enable Clone, even for Global Instance.
            menu.add_command(label="Clone", command=self.clone_selected_main)
            menu.add_command(label="Open Folder", command=self.open_selected_main)
            menu.tk_popup(event.x_root, event.y_root)
            menu.grab_release()

    def delete_selected_main(self):
        path = self.get_selected_instance_path()
        if path and delete_instance(path):
            self.populate_instances()

    def clone_selected_main(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            instance_name = item["values"][0]
            clone_instance(instance_name, self.game)
            self.populate_instances()

    def open_selected_main(self):
        path = self.get_selected_instance_path()
        if path:
            open_instance_folder(path)

    def manage_instances_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Manage Instances")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)

        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            listbox.delete(0, tk.END)
            global_install = find_install_location(self.game)
            if global_install:
                global_info = get_global_instance_info(self.game)
                listbox.insert(tk.END, global_info.get("instance", "Global Instance"))
            for instance in list_instances(self.game):
                listbox.insert(tk.END, instance)

        refresh_list()

        # Right-click context for Instances listbox
        instance_menu = tk.Menu(listbox, tearoff=0)
        instance_menu.add_command(label="Delete", command=lambda: delete_inst())
        instance_menu.add_command(label="Clone", command=lambda: clone_inst())
        instance_menu.add_command(label="Open Folder", command=lambda: open_inst())

        def show_inst_menu(event):
            index = listbox.nearest(event.y)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            inst = listbox.get(index)
            if inst == "Global Instance":
                instance_menu.entryconfig("Delete", state="disabled")
            else:
                instance_menu.entryconfig("Delete", state="normal")
            instance_menu.tk_popup(event.x_root, event.y_root)
            instance_menu.grab_release()

        listbox.bind("<Button-3>", show_inst_menu)

        def delete_inst():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No instance selected.")
                return
            instance_name = listbox.get(sel[0])
            if instance_name == "Global Instance":
                custom_error(dialog, "Error", "Cannot delete the Global Instance.")
                return
            instance_path = os.path.join(self.game["INSTANCES_DIR"], instance_name)
            if centered_askyesno(self.winfo_toplevel(), "Confirm Delete", f"Delete instance '{instance_name}'?"):
                try:
                    shutil.rmtree(instance_path)
                    refresh_list()
                    self.populate_instances()
                except Exception as e:
                    custom_error(dialog, "Error", f"Failed to delete instance: {e}")

        def clone_inst():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No instance selected.")
                return
            inst = listbox.get(sel[0])
            clone_instance(inst, self.game)
            refresh_list()
            self.populate_instances()

        def open_inst():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No instance selected.")
                return
            inst = listbox.get(sel[0])
            if inst == "Global Instance":
                folder = find_install_location(self.game)
                if not folder:
                    custom_error(dialog, "Error", "Installation not found.")
                    return
            else:
                folder = os.path.join(self.game["INSTANCES_DIR"], inst)
            if os.path.exists(folder):
                subprocess.Popen(["explorer", folder])
            else:
                custom_error(dialog, "Error", "Folder not found.")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Create New", command=lambda: [self.new_instance_dialog(), refresh_list()]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        dialog.wait_window()
        self.populate_instances()

    def new_instance_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Instance")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)

        tk.Label(dialog, text="Instance Name:").pack(pady=5)
        instance_var = tk.StringVar()
        tk.Entry(dialog, textvariable=instance_var).pack(pady=5)

        error_label = tk.Label(dialog, text="", fg="red")
        error_label.pack(pady=5)

        tk.Label(dialog, text="Version:").pack(pady=5)
        custom_versions = get_version_options(self.game)
        if not custom_versions:
            custom_error(tk._default_root, "Error", "No versions available. Please create a new version first.")
            dialog.destroy()
            return
        selected_version = tk.StringVar(dialog)
        selected_version.set(custom_versions[0])
        tk.OptionMenu(dialog, selected_version, *custom_versions).pack(pady=5)

        def on_create():
            inst_name = instance_var.get().strip()
            if not inst_name:
                error_label.config(text="Instance name cannot be empty.")
                return
            if len(inst_name) > 25:
                error_label.config(text="Instance name cannot exceed 25 characters.")
                return
            if os.path.exists(os.path.join(self.game["INSTANCES_DIR"], inst_name)):
                error_label.config(text="An instance with that name already exists.")
                return
            ver = selected_version.get()
            force_copy = False
            if ver == self.game["VANILLA_VERSION"]:
                proceed = centered_askyesno(dialog, "Confirm",
                    "Using this version may lead to issues if you have existing mods or classic installed.\n"
                    "Please verify your CastleMiner game files if you have not already.\n"
                    "Do you wish to continue?", height=175)
                if not proceed:
                    return
                else:
                    force_copy = True
            result = create_instance(inst_name, ver, self.game, force_copy=force_copy)
            if result is None or result == "exists":
                error_label.config(text="Failed to create instance.")
            else:
                self.populate_instances()
                dialog.destroy()

        tk.Button(dialog, text="Create Instance", command=on_create).pack(pady=10)
        dialog.wait_window()

    def new_version_dialog(self):
        new_version_dialog(self.game, self)

    def populate_instances(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        global_install = find_install_location(self.game)
        if global_install:
            global_info = get_global_instance_info(self.game)
            self.tree.insert("", "end", values=(global_info.get("instance", "Global Instance"),
                                                 global_info.get("version", self.game["VANILLA_VERSION"]),
                                                 global_info.get("last_played", "")))
        for inst in list_instances(self.game):
            inst_path = os.path.join(self.game["INSTANCES_DIR"], inst)
            info_file = os.path.join(inst_path, "instance_info.json")
            if os.path.exists(info_file):
                try:
                    with open(info_file, "r") as f:
                        info = json.load(f)
                except Exception:
                    info = {"instance": inst, "version": "", "last_played": ""}
            else:
                info = {"instance": inst, "version": "", "last_played": ""}
            self.tree.insert("", "end", values=(info.get("instance", inst),
                                                 info.get("version", ""),
                                                 info.get("last_played", "")))
        self.sort_tree(self.sort_column, self.sort_reverse)
        self.set_action_buttons_state(True)

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.sort_tree(self.sort_column, self.sort_reverse)

    def sort_tree(self, col, reverse):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        if col == "last_played":
            def conv(x):
                try:
                    return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    return datetime.datetime.min
            items = [(conv(val), k) for (val, k) in items]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

    def on_instance_select(self, event):
        if self.tree.selection():
            self.play_btn.config(state=tk.NORMAL)
            self.open_btn.config(state=tk.NORMAL)
        else:
            self.set_action_buttons_state(False)

    def set_action_buttons_state(self, state):
        st = tk.NORMAL if state else tk.DISABLED
        self.play_btn.config(state=st)
        self.open_btn.config(state=st)

    def get_selected_instance_path(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            inst_name = item["values"][0]
            if inst_name == "Global Instance":
                return find_install_location(self.game)
            else:
                return os.path.join(self.game["INSTANCES_DIR"], inst_name)
        return None

    def start_instance(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            inst_name = item["values"][0]
            path = self.get_selected_instance_path()
            if path:
                launch_game(path, self.game)
                if inst_name == "Global Instance":
                    global_info = get_global_instance_info(self.game)
                    global_info["last_played"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    write_global_instance_info(self.game, global_info)
                else:
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

    def manage_versions_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Manage Versions")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, self)

        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        def refresh_list():
            listbox.delete(0, tk.END)
            versions = get_version_options(self.game)
            for v in versions:
                listbox.insert(tk.END, v)

        refresh_list()

        version_menu = tk.Menu(listbox, tearoff=0)
        version_menu.add_command(label="Delete", command=lambda: delete_version())
        version_menu.add_command(label="Clone", command=lambda: in_clone_version())
        version_menu.add_command(label="Open Folder", command=lambda: open_version())

        def show_version_menu(event):
            index = listbox.nearest(event.y)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            ver = listbox.get(index)
            if ver == self.game["VANILLA_VERSION"]:
                version_menu.entryconfig("Delete", state="disabled")
            else:
                version_menu.entryconfig("Delete", state="normal")
            version_menu.tk_popup(event.x_root, event.y_root)
            version_menu.grab_release()

        listbox.bind("<Button-3>", show_version_menu)

        def delete_version():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            ver = listbox.get(sel[0])
            if ver == self.game["VANILLA_VERSION"]:
                custom_error(dialog, "Error", "Cannot delete the vanilla version.")
                return
            ver_path = os.path.join(self.game["VERSIONS_DIR"], ver)
            if centered_askyesno(self.winfo_toplevel(), "Confirm Delete", f"Delete version '{ver}'?"):
                try:
                    shutil.rmtree(ver_path)
                    refresh_list()
                except Exception as e:
                    custom_error(dialog, "Error", f"Failed to delete version: {e}")

        def in_clone_version():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            ver = listbox.get(sel[0])
            clone_version(ver, self.game)  # calls helper
            refresh_list()

        def open_version():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            ver = listbox.get(sel[0])
            if ver == self.game["VANILLA_VERSION"]:
                folder = find_install_location(self.game)
                if not folder:
                    custom_error(dialog, "Error", "Installation not found.")
                    return
            else:
                folder = os.path.join(self.game["VERSIONS_DIR"], ver)
            if os.path.exists(folder):
                subprocess.Popen(["explorer", folder])
            else:
                custom_error(dialog, "Error", "Folder not found.")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Create New", command=lambda: [self.new_version_dialog(), refresh_list()]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
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
    for game in games.values():
        ensure_game_folders(game)


if __name__ == "__main__":
    initial_setup()
    app = LauncherGUI()
    app.mainloop()
