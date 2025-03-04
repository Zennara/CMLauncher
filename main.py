import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

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
        # For auto-detection, we assume common install paths:
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
    # We'll check if the cache folder exists and is nonempty.
    if not os.path.exists(cache_dir) or not os.listdir(cache_dir):
        print(f"[INFO] Caching base game from: {base_game_path}")
        # If cache folder exists but is empty, remove it to allow copytree.
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


def auto_detect_install_location(game):
    """
    Attempt to auto-detect the installation location.
    If found, ask the user to confirm.
    If not, prompt the user to input it manually.
    """
    install_path = find_install_location(game)
    if install_path:
        if messagebox.askyesno("Confirm Install Location",
                               f"Detected installation at:\n{install_path}\nIs this correct?"):
            return install_path
    # If auto-detection fails or user declines, ask for manual entry.
    manual_path = simpledialog.askstring("Install Location",
                                         f"Enter the full path to your installation of {game}:")
    return manual_path


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


def create_instance(instance_name, version, game):
    """
    Create a new instance with the given name and version.
    It is created by copying the GAME_CACHE and then overlaying version files.
    """
    instance_path = os.path.join(game["INSTANCES_DIR"], instance_name)
    if os.path.exists(instance_path):
        messagebox.showerror("Error", f"An instance named '{instance_name}' already exists!")
        return None

    try:
        print(f"[INFO] Creating new instance '{instance_name}' with version '{version}'...")
        shutil.copytree(game["GAME_CACHE"], instance_path)
        overlay_version_files(instance_path, version, game)
        return instance_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create instance: {e}")
        return None


def launch_game(instance_path, game):
    """Launch the game from the given instance folder."""
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
        messagebox.showerror("Error", "Game executable not found in the instance folder.")


def open_instance_folder(instance_path):
    """Open the instance folder in Windows Explorer."""
    if os.path.exists(instance_path):
        subprocess.Popen(["explorer", instance_path])
    else:
        messagebox.showerror("Error", "Instance folder not found.")


def delete_instance(instance_path):
    """Delete the given instance folder after confirmation."""
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this instance?"):
        try:
            shutil.rmtree(instance_path)
            messagebox.showinfo("Deleted", "Instance deleted successfully.")
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


# ----------------------------
# GUI Classes
# ----------------------------

class HomeTab(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = tk.Label(self, text="Welcome to CMLauncher!\n\n"
                                    "This launcher allows you to manage multiple instances "
                                    "of your games and apply different versions/modifications.\n\n"
                                    "Use the tabs above to manage each game. For a game tab to work, "
                                    "its base game must be cached. If not, the launcher will attempt to auto-detect "
                                    "the installation and prompt you accordingly.\n\n"
                                    "Enjoy!", justify=tk.LEFT)
        label.pack(padx=20, pady=20, anchor="w")


class GameTab(tk.Frame):
    def __init__(self, master, game_name, game):
        super().__init__(master)
        self.game_name = game_name
        self.game = game
        ensure_game_folders(self.game)
        self.create_widgets()
        self.populate_instances()
        self.check_base_game()

    def create_widgets(self):
        header = tk.Label(self, text=self.game_name, font=("Arial", 16))
        header.pack(pady=5)

        # Label to display base game status
        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack(pady=5)

        # Verify button will appear if base game not cached.
        self.verify_button = tk.Button(self, text="Verify Base Game", command=self.verify_base_game)
        self.verify_button.pack(pady=5)

        # Instance list and controls
        self.instance_listbox = tk.Listbox(self, height=10)
        self.instance_listbox.pack(fill=tk.BOTH, expand=True, padx=20)
        self.instance_listbox.bind("<<ListboxSelect>>", self.on_instance_select)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        new_btn = tk.Button(btn_frame, text="New Instance", command=self.new_instance_dialog)
        new_btn.grid(row=0, column=0, padx=5)
        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start_instance, state=tk.DISABLED)
        self.start_btn.grid(row=0, column=1, padx=5)
        self.open_btn = tk.Button(btn_frame, text="Open Folder", command=self.open_instance, state=tk.DISABLED)
        self.open_btn.grid(row=0, column=2, padx=5)
        self.delete_btn = tk.Button(btn_frame, text="Delete", command=self.delete_instance, state=tk.DISABLED)
        self.delete_btn.grid(row=0, column=3, padx=5)

    def check_base_game(self):
        # Check if base game is cached (i.e. GAME_CACHE exists and is non-empty)
        cache_dir = self.game["GAME_CACHE"]
        if not os.path.exists(cache_dir) or not os.listdir(cache_dir):
            self.status_label.config(text="Base game not cached!")
            self.disable_instance_controls()
        else:
            self.status_label.config(text="Base game cached.")
            self.enable_instance_controls()

    def verify_base_game(self):
        # Try auto-detection; if it fails, ask manually.
        detected = find_install_location(self.game)
        if detected:
            if messagebox.askyesno("Confirm", f"Detected installation at:\n{detected}\nCache base game from here?"):
                cache_base_game_for_game(detected, self.game)
        else:
            manual = simpledialog.askstring("Install Location", f"Enter full path to {self.game_name} installation:")
            if manual and os.path.exists(os.path.join(manual, self.game["EXE_NAME"])):
                cache_base_game_for_game(manual, self.game)
            else:
                messagebox.showerror("Error", "Invalid installation path provided.")
        self.check_base_game()
        self.populate_instances()

    def new_instance_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Instance")
        dialog.geometry("300x200")

        tk.Label(dialog, text="Instance Name:").pack(pady=5)
        name_entry = tk.Entry(dialog)
        name_entry.pack(pady=5)

        tk.Label(dialog, text="Version:").pack(pady=5)
        version_options = get_version_options(self.game)
        selected_version = tk.StringVar(dialog)
        selected_version.set(version_options[0])
        version_menu = tk.OptionMenu(dialog, selected_version, *version_options)
        version_menu.pack(pady=5)

        def on_create():
            instance_name = name_entry.get().strip()
            version = selected_version.get()
            if not instance_name:
                messagebox.showwarning("Warning", "Instance name cannot be empty.", parent=dialog)
                return
            path = create_instance(instance_name, version, self.game)
            if path:
                messagebox.showinfo("Success", f"Instance '{instance_name}' created.")
                self.populate_instances()
                dialog.destroy()

        tk.Button(dialog, text="Create Instance", command=on_create).pack(pady=10)

    def populate_instances(self):
        self.instance_listbox.delete(0, tk.END)
        for instance in list_instances(self.game):
            self.instance_listbox.insert(tk.END, instance)
        self.set_action_buttons_state(False)

    def on_instance_select(self, event):
        if self.instance_listbox.curselection():
            self.set_action_buttons_state(True)
        else:
            self.set_action_buttons_state(False)

    def set_action_buttons_state(self, state):
        st = tk.NORMAL if state else tk.DISABLED
        self.start_btn.config(state=st)
        self.open_btn.config(state=st)
        self.delete_btn.config(state=st)

    def get_selected_instance_path(self):
        sel = self.instance_listbox.curselection()
        if sel:
            instance_name = self.instance_listbox.get(sel[0])
            return os.path.join(self.game["INSTANCES_DIR"], instance_name)
        return None

    def start_instance(self):
        path = self.get_selected_instance_path()
        if path:
            launch_game(path, self.game)

    def open_instance(self):
        path = self.get_selected_instance_path()
        if path:
            open_instance_folder(path)

    def delete_instance(self):
        path = self.get_selected_instance_path()
        if path and delete_instance(path):
            self.populate_instances()

    # New methods added to enable/disable controls.
    def enable_instance_controls(self):
        self.start_btn.config(state=tk.NORMAL)
        self.open_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)

    def disable_instance_controls(self):
        self.start_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.delete_btn.config(state=tk.DISABLED)


class LauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMLauncher")
        self.geometry("600x500")
        self.create_tabs()

    def create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Home tab
        home_tab = HomeTab(notebook)
        notebook.add(home_tab, text="Home")

        # For each game, create a tab.
        for game_name, game in games.items():
            game_tab = GameTab(notebook, game_name, game)
            notebook.add(game_tab, text=game_name)


def initial_setup():
    """Perform initial setup: create required folders for each game and try auto-detect caching if possible."""
    for game in games.values():
        ensure_game_folders(game)
    # For each game, if its base game is not cached, try auto-detect.
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
