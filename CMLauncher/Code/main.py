import os
import shutil
import subprocess
import tkinter as tk
import webbrowser
from tkinter import ttk, scrolledtext
import tkinter.font as tkFont
import json
import datetime

from config import MANAGE_ICON, PLUS_ICON, BASE_ICON
from config import LOCAL_VERSION, LOCAL_INSTANCE, games, INSTALL_PATHS_FILE
from custom_windows import custom_error, custom_validated_askstring, centered_askyesno, center_window, custom_askstring, \
    custom_info
from instance_info import write_instance_info, get_instance_info, get_global_instance_info, write_global_instance_info

def read_install_paths():
    if os.path.exists(INSTALL_PATHS_FILE):
        with open(INSTALL_PATHS_FILE, "r") as f:
            return json.load(f)
    return {}

def write_install_paths(paths):
    with open(INSTALL_PATHS_FILE, "w") as f:
        json.dump(paths, f, indent=4)

def check_install_paths():
    paths = read_install_paths()
    updated_paths = {}
    for game_name, path in paths.items():
        exe_path = os.path.join(path, games[game_name]["EXE_NAME"])
        if os.path.exists(exe_path):
            updated_paths[game_name] = path
    if updated_paths != paths:
        write_install_paths(updated_paths)
    return updated_paths


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


def overlay_version_files(instance_path, version, game):
    """
    Overlay version-specific files onto an instance folder.
    If version is the vanilla version, do nothing.
    Otherwise, overlay files from the Versions folder.
    """
    if version == LOCAL_VERSION:
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
        if version == LOCAL_VERSION:
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
        app_id = game["APP_ID"]
        f.write(str(app_id))
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
            if os.path.isdir(os.path.join(game["INSTANCES_DIR"], instance)) and instance != LOCAL_INSTANCE]


def get_version_options(game):
    """Return a list of available versions (vanilla plus folders in Versions)."""
    options = [LOCAL_VERSION]
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
    dialog.iconbitmap(MANAGE_ICON)
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
        if version_name == LOCAL_VERSION:
            error_label.config(text="Cannot use 'Steam Version' as a version name.")
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
    if instance_name == LOCAL_INSTANCE:
        source = find_install_location(game)
        if not source:
            custom_error(tk._default_root, "Error", "Global Instance source not found.")
            return
    else:
        source = os.path.join(game["INSTANCES_DIR"], instance_name)

    def validate_instance_name(name):
        if not name:
            return "Instance name cannot be empty."
        if name == LOCAL_INSTANCE:
            return "Cannot use 'Global Instance' as an instance name."
        if len(name) > 25:
            return "Instance name cannot exceed 25 characters."
        new_path = os.path.join(game["INSTANCES_DIR"], name)
        if os.path.exists(new_path):
            return "An instance with that name already exists."
        return None

    new_name = custom_validated_askstring(tk._default_root, "Clone Instance",
                                          "Enter new instance name:", validate_instance_name)
    if not new_name:
        return
    new_path = os.path.join(game["INSTANCES_DIR"], new_name)
    try:
        shutil.copytree(source, new_path)
        info = get_instance_info(new_path)
        info["instance"] = new_name
        if instance_name == LOCAL_INSTANCE:
            info["version"] = LOCAL_VERSION
        info["last_played"] = ""
        write_instance_info(new_path, info)
        custom_info(tk._default_root, "Clone", f"Instance cloned as '{new_name}'.")
    except Exception as e:
        custom_error(tk._default_root, "Error", f"Failed to clone instance: {e}")

def clone_version(version_name, game):
    """Clone a version folder with a new name (including the vanilla version)."""
    if version_name == LOCAL_VERSION:
        source = find_install_location(game)
        if not source:
            custom_error(tk._default_root, "Error", "Installation for vanilla version not found.")
            return
    else:
        source = os.path.join(game["VERSIONS_DIR"], version_name)
    def validate_version_name(name):
        if not name:
            return "Version name cannot be empty."
        if name == LOCAL_VERSION:
            return "Cannot use 'Steam Version' as a version name."
        if len(name) > 25:
            return "Version name cannot exceed 25 characters."
        new_path = os.path.join(game["VERSIONS_DIR"], name)
        if os.path.exists(new_path):
            return "A version with that name already exists."
        return None
    new_name = custom_validated_askstring(tk._default_root, "Clone Version",
                                          "Enter new version name:", validate_version_name)
    if not new_name:
        return
    new_path = os.path.join(game["VERSIONS_DIR"], new_name)
    try:
        shutil.copytree(source, new_path)
        custom_info(tk._default_root, "Clone", f"Version cloned as '{new_name}'.")
    except Exception as e:
        custom_error(tk._default_root, "Error", f"Failed to clone version: {e}")



# ----------------------------
# GUI Classes
# ----------------------------
class HomeTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Create a scrolled text widget with word wrapping.
        self.text_widget = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=80, height=5)
        self.text_widget.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Define fonts for different text sizes.
        base_font = tkFont.Font(family="Helvetica", size=12)
        h1_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        h2_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        h3_font = tkFont.Font(family="Helvetica", size=14, weight="bold")

        # Configure text tags to simulate Markdown styling.
        self.text_widget.tag_configure("h1", font=h1_font, spacing1=10, spacing3=10)
        self.text_widget.tag_configure("h2", font=h2_font, spacing1=8, spacing3=8)
        self.text_widget.tag_configure("h3", font=h3_font, spacing1=6, spacing3=6)
        self.text_widget.tag_configure("body", font=base_font, spacing1=4, spacing3=4)

        # Insert text with tags to simulate Markdown content.
        self.text_widget.insert(tk.END, "CMLauncher\n", "h1")
        self.text_widget.insert(tk.END,
                                "Thank you for using CMLauncher! Below you will find some information regarding terminology, and how to use various features of the launcher.\n", "body")

        self.text_widget.insert(tk.END, "\n")
        self.text_widget.insert(tk.END, "Versions\n", "h3")
        self.text_widget.insert(tk.END,
                                "Versions are complete, full versions of the CM game and all of its required files. Your Steam "
                                "Version is your currently installed Steam version of the game. This can change if you directly "
                                "modify your game files without use of this launcher.\n", "body")

        self.text_widget.insert(tk.END, "Instances\n", "h3")
        self.text_widget.insert(tk.END,
                                "Instances are created from versions. After creation, an instance's files can be edited (mods can be "
                                "installed, as well) without affecting its associated Version.\n", "body")

        self.text_widget.insert(tk.END, "\n")

        self.text_widget.insert(tk.END, "First Launch\n", "h3")
        self.text_widget.insert(tk.END,
                                "On your first launch of CMLauncher, the launcher will attempt to locate your CM game directories "
                                "automatically. If it fails, you will need to set up the installation path for each game manually on its "
                                "respective tab.\n", "body")

        self.text_widget.insert(tk.END, "General\n", "h3")
        self.text_widget.insert(tk.END,
                                "Modify your existing Versions/Instances or create new ones by clicking their respective buttons. "
                                "From there, you can right-click to perform specific functions on them.\n", "body")

        self.text_widget.insert(tk.END, "\n")

        self.text_widget.insert(tk.END, "Installing Mods\n", "h3")
        self.text_widget.insert(tk.END, "To install a modded version to a launcher version follow these steps:\n",
                                "body")
        self.text_widget.insert(tk.END,
                                "1. Create the appropriate base game Version for the modded client, if you have not already.\n",
                                "body")
        self.text_widget.insert(tk.END, "2. Create a new Instance for your mod, if you do not have one already. ",
                                "body")
        self.text_widget.insert(tk.END, "Tip: You can create new Instances for each mod version.\n", "body")
        self.text_widget.insert(tk.END, "3. Open the folder location for your created Instance.\n", "body")
        self.text_widget.insert(tk.END,
                                "4. Copy and replace all of the mod files (or follow mod-specific installation instructions).\n",
                                "body")
        self.text_widget.insert(tk.END, "5. Select the instance, and play!\n", "body")

        self.text_widget.insert(tk.END, "\n")

        self.text_widget.insert(tk.END, "Report a Bug / Request Feature\n", "h2")
        self.text_widget.insert(tk.END, "If you encounter a bug, or have a feature request, please report it at our issues page on GitHub.\n", "body")

        self.text_widget.insert(tk.END, "Contributing\n", "h2")
        self.text_widget.insert(tk.END, "Contributions are always welcome! You can do so on our GitHub.\n", "body")

        # Make the text widget read-only.
        self.text_widget.configure(state='disabled')

        # Create a frame for the buttons (preserving your original button code).
        button_frame = tk.Frame(self)
        button_frame.pack(padx=20, pady=10)

        # GitHub button that opens the GitHub page.
        github_button = tk.Button(
            button_frame,
            text="GitHub",
            command=lambda: webbrowser.open("https://github.com/zennara/CMLauncher")
        )
        github_button.pack(side=tk.LEFT, padx=10)

        github_button = tk.Button(
            button_frame,
            text="Issue/Request",
            command=lambda: webbrowser.open("https://github.com/zennara/CMLauncher/issues")
        )
        github_button.pack(side=tk.LEFT, padx=10)

        # Discord button that opens the Discord invite.
        discord_button = tk.Button(
            button_frame,
            text="Discord",
            command=lambda: webbrowser.open("https://discord.gg/cJH7DFb")
        )
        discord_button.pack(side=tk.LEFT, padx=10)

        copyright_info = "© 2025 Zennara. Licensed under the Apache License, Version 2.0."
        info_label = tk.Label(self, text=copyright_info, wraplength=500, justify=tk.LEFT)
        info_label.pack(padx=20, pady=(10, 20))


class GameTab(tk.Frame):
    def __init__(self, master, game_name, game):
        super().__init__(master)
        self.game_name = game_name
        self.game = game
        ensure_game_folders(self.game)
        self.sort_column = "instance"
        self.sort_reverse = False

        install_paths = check_install_paths()
        if game_name in install_paths:
            self.game["POSSIBLE_PATHS"].insert(0, install_paths[game_name])

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
        path = custom_askstring(tk._default_root, "Set Installation Path",
                                f"Enter the Steam installation path for {self.game_name}:")
        if path:
            exe_path = os.path.join(path, self.game["EXE_NAME"])
            if os.path.exists(exe_path):
                self.game["POSSIBLE_PATHS"].insert(0, path)
                install_paths = read_install_paths()
                install_paths[self.game_name] = path
                write_install_paths(install_paths)
                for widget in self.winfo_children():
                    widget.destroy()
                self.create_widgets()
                self.populate_instances()
            else:
                custom_error(tk._default_root, "Error", f"Executable not found at provided path:\n{exe_path}")

    def create_widgets(self):
        header = tk.Label(self, text=self.game_name, font=("Arial", 16))
        header.pack(pady=(15, 1))

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=10)

        self.versions_btn = tk.Button(bottom_frame, text="Versions", command=self.manage_versions_dialog)
        self.versions_btn.pack(side=tk.RIGHT, padx=20)

        self.instances_btn = tk.Button(bottom_frame, text="Instances", command=self.manage_instances_dialog)
        self.instances_btn.pack(side=tk.LEFT, padx=20)

        self.tree = ttk.Treeview(self, columns=("instance", "version", "last_played"), show="headings")
        self.tree.heading("instance", text="Instance", command=lambda: self.sort_by("instance"))
        self.tree.heading("version", text="Version", command=lambda: self.sort_by("version"))
        self.tree.heading("last_played", text="Last Played", command=lambda: self.sort_by("last_played"))
        self.tree.column("instance", anchor="w", width=150)
        self.tree.column("version", anchor="w", width=100)
        self.tree.column("last_played", anchor="w", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_instance_select)

        self.play_btn = tk.Button(self, text="   Play   ", command=self.start_instance, state=tk.DISABLED,
                                  font=("Arial", 18))
        self.play_btn.pack(pady=(10, 0))

        self.selected_instance_label = tk.Label(self, text="No instance selected", font=("Arial", 10))
        self.selected_instance_label.pack(pady=(5, 15))

    def open_selected_main(self):
        path = self.get_selected_instance_path()
        if path:
            open_instance_folder(path)

    def manage_instances_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Manage Instances")
        dialog.geometry("400x300")
        dialog.iconbitmap(MANAGE_ICON)
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
                listbox.insert(tk.END, global_info.get("instance", LOCAL_INSTANCE))
            for instance in list_instances(self.game):
                listbox.insert(tk.END, instance)

        refresh_list()

        # Right-click context for Instances listbox
        instance_menu = tk.Menu(listbox, tearoff=0)
        instance_menu.add_command(label="Rename", command=lambda: rename_inst())
        instance_menu.add_command(label="Delete", command=lambda: delete_inst())
        instance_menu.add_command(label="Clone", command=lambda: clone_inst())
        instance_menu.add_command(label="Open Folder", command=lambda: open_inst())

        def show_inst_menu(event):
            index = listbox.nearest(event.y)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(index)
            inst = listbox.get(index)
            instance_menu = tk.Menu(listbox, tearoff=0)
            if inst != LOCAL_INSTANCE:
                instance_menu.add_command(label="Rename", command=lambda: rename_inst())
                instance_menu.add_command(label="Delete", command=lambda: delete_inst())
            instance_menu.add_command(label="Clone", command=lambda: clone_inst())
            instance_menu.add_command(label="Open Folder", command=lambda: open_inst())
            instance_menu.tk_popup(event.x_root, event.y_root)
            instance_menu.grab_release()

        listbox.bind("<Button-3>", show_inst_menu)

        def rename_inst():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No instance selected.")
                return
            inst = listbox.get(sel[0])
            if inst == LOCAL_INSTANCE:
                custom_error(dialog, "Error", "Cannot rename the Global Instance.")
                return

            def validate_instance_name(name):
                if not name:
                    return "Instance name cannot be empty."
                if name == LOCAL_INSTANCE:
                    return "Cannot use 'Global Instance' as an instance name."
                if len(name) > 25:
                    return "Instance name cannot exceed 25 characters."
                new_path = os.path.join(self.game["INSTANCES_DIR"], name)
                if os.path.exists(new_path):
                    return "An instance with that name already exists."
                return None

            new_name = custom_validated_askstring(tk._default_root, "Rename Instance", "Enter new instance name:",
                                                  validate_instance_name)
            if not new_name:
                return
            old_path = os.path.join(self.game["INSTANCES_DIR"], inst)
            new_path = os.path.join(self.game["INSTANCES_DIR"], new_name)
            try:
                os.rename(old_path, new_path)

                # Update the instance metadata with the new name
                info = get_instance_info(new_path)
                info["instance"] = new_name
                write_instance_info(new_path, info)

                refresh_list()
                self.populate_instances()
            except Exception as e:
                custom_error(tk._default_root, "Error", f"Failed to rename instance: {e}")

        def delete_inst():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No instance selected.")
                return
            instance_name = listbox.get(sel[0])
            if instance_name == LOCAL_INSTANCE:
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
            if inst == LOCAL_INSTANCE:
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
        dialog.iconbitmap(PLUS_ICON)
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
            if inst_name == LOCAL_INSTANCE:
                error_label.config(text="Cannot use 'Global Instance' as an instance name.")
                return
            if len(inst_name) > 25:
                error_label.config(text="Instance name cannot exceed 25 characters.")
                return
            if os.path.exists(os.path.join(self.game["INSTANCES_DIR"], inst_name)):
                error_label.config(text="An instance with that name already exists.")
                return
            ver = selected_version.get()
            force_copy = False
            if ver == LOCAL_VERSION:
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
            self.tree.insert("", "end", values=(global_info.get("instance", LOCAL_INSTANCE),
                                                 global_info.get("version", LOCAL_VERSION),
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
        self.set_action_buttons_state(False)

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
            item = self.tree.item(self.tree.selection()[0])
            inst_name = str(item["values"][0])
            self.selected_instance_label.config(text=inst_name)
            self.play_btn.config(state=tk.NORMAL)
        else:
            self.selected_instance_label.config(text="No instance selected")
            self.play_btn.config(state=tk.DISABLED)

    def set_action_buttons_state(self, state):
        st = tk.NORMAL if state else tk.DISABLED
        self.play_btn.config(state=st)

    def get_selected_instance_path(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            inst_name = str(item["values"][0])
            if inst_name == LOCAL_INSTANCE:
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
                if inst_name == LOCAL_INSTANCE:
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
        dialog.iconbitmap(MANAGE_ICON)
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
            version_menu = tk.Menu(listbox, tearoff=0)
            if ver != LOCAL_VERSION:
                version_menu.add_command(label="Delete", command=lambda: delete_version())
            version_menu.add_command(label="Clone", command=lambda: in_clone_version())
            version_menu.add_command(label="Open Folder", command=lambda: open_version())
            version_menu.tk_popup(event.x_root, event.y_root)
            version_menu.grab_release()

        listbox.bind("<Button-3>", show_version_menu)

        def rename_selected_version():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            ver = listbox.get(sel[0])
            if ver == LOCAL_VERSION:
                custom_error(dialog, "Error", "Cannot rename the vanilla version.")
                return

            def validate_version_name(name):
                if not name:
                    return "Version name cannot be empty."
                if name == LOCAL_VERSION:
                    return "Cannot use 'Steam Version' as a version name."
                if len(name) > 25:
                    return "Version name cannot exceed 25 characters."
                new_path = os.path.join(self.game["VERSIONS_DIR"], name)
                if os.path.exists(new_path):
                    return "A version with that name already exists."
                return None

            new_name = custom_validated_askstring(tk._default_root, "Rename Version", "Enter new version name:",
                                                  validate_version_name)
            if not new_name:
                return
            old_path = os.path.join(self.game["VERSIONS_DIR"], ver)
            new_path = os.path.join(self.game["VERSIONS_DIR"], new_name)
            try:
                os.rename(old_path, new_path)
                custom_info(tk._default_root, "Rename", f"Version renamed to '{new_name}'.")

                # Update metadata in all instances that reference the old version:
                def update_instances_version(game, old_ver, new_ver):
                    for inst in list_instances(game):
                        inst_path = os.path.join(game["INSTANCES_DIR"], inst)
                        info = get_instance_info(inst_path)
                        if info.get("version") == old_ver:
                            info["version"] = new_ver
                            write_instance_info(inst_path, info)

                update_instances_version(self.game, ver, new_name)
                refresh_list()
            except Exception as e:
                custom_error(tk._default_root, "Error", f"Failed to rename version: {e}")

        def delete_version():
            sel = listbox.curselection()
            if not sel:
                custom_error(dialog, "Error", "No version selected.")
                return
            ver = listbox.get(sel[0])
            if ver == LOCAL_VERSION:
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
            if ver == LOCAL_VERSION:
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
        self.iconbitmap(BASE_ICON)
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
