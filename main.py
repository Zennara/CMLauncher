import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox

# Paths (customize these to your setup)
BASE_DIR = r"C:\Users\Keagan\Desktop\CMLauncher"
GAME_CACHE = os.path.join(BASE_DIR, "GameCache")       # Full base game cache
MODS_DIR = os.path.join(BASE_DIR, "Mods")              # Mod files (only changes)
WORKING_DIRS = os.path.join(BASE_DIR, "WorkingDirs")   # Persistent mod instances
BASE_GAME_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z"

def cache_base_game(base_game_path):
    """ Cache the base game if it's not cached already """
    if not os.path.exists(GAME_CACHE):
        print("[INFO] Caching base game...")
        shutil.copytree(base_game_path, GAME_CACHE)
    else:
        print("[INFO] Base game already cached.")

def setup_mod_environment(mod_name):
    """
    Create or update an isolated working directory for the selected mod.
    If the working directory already exists, it is reused (so any new files
    created by the game remain), and mod overlay files are updated.
    """
    mod_path = os.path.join(MODS_DIR, mod_name)
    mod_working_dir = os.path.join(WORKING_DIRS, mod_name)

    if not os.path.exists(mod_path):
        print(f"[ERROR] Mod '{mod_name}' not found!")
        return None

    # If the working directory doesn't exist, create it by copying the cached game.
    if not os.path.exists(mod_working_dir):
        print(f"[INFO] Creating new working directory for '{mod_name}'...")
        shutil.copytree(GAME_CACHE, mod_working_dir)
    else:
        print(f"[INFO] Reusing existing working directory for '{mod_name}'.")

    # Overlay mod-specific files (this will update files that the mod provides)
    for root, _, files in os.walk(mod_path):
        for file in files:
            relative_path = os.path.relpath(root, mod_path)
            dest_path = os.path.join(mod_working_dir, relative_path, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(os.path.join(root, file), dest_path)
            print(f"[INFO] Overlaying file: {dest_path}")

    return mod_working_dir

def launch_game(working_dir):
    """ Launch CastleMiner Z from the persistent working directory with steam_appid.txt. """
    game_exe = os.path.join(working_dir, "CastleMinerZ.exe")
    app_id_path = os.path.join(working_dir, "steam_appid.txt")

    # Ensure steam_appid.txt exists
    with open(app_id_path, "w") as f:
        f.write("253430")

    if os.path.exists(game_exe):
        print("[INFO] Launching game with isolated files...")
        env = os.environ.copy()
        env["PATH"] = working_dir + ";" + env["PATH"]
        env["PWD"] = working_dir

        # Use Popen to launch the game without blocking the GUI.
        subprocess.Popen(game_exe, cwd=working_dir, env=env)
    else:
        print("[ERROR] Game executable not found!")
        messagebox.showerror("Error", "Game executable not found in working directory.")

def list_mods():
    """ List available mods """
    if not os.path.exists(MODS_DIR):
        os.makedirs(MODS_DIR)
    return [mod for mod in os.listdir(MODS_DIR) if os.path.isdir(os.path.join(MODS_DIR, mod))]

class LauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CastleMiner Z Launcher")
        self.geometry("400x300")
        self.create_widgets()
        self.populate_mods()
        # Cache the base game when the GUI starts
        cache_base_game(BASE_GAME_PATH)

    def create_widgets(self):
        label = tk.Label(self, text="Select a Mod:")
        label.pack(pady=10)

        self.mod_listbox = tk.Listbox(self, height=10)
        self.mod_listbox.pack(fill=tk.BOTH, expand=True, padx=20)

        launch_button = tk.Button(self, text="Launch Mod", command=self.launch_selected_mod)
        launch_button.pack(pady=10)

    def populate_mods(self):
        mods = list_mods()
        for mod in mods:
            self.mod_listbox.insert(tk.END, mod)

    def launch_selected_mod(self):
        selection = self.mod_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a mod to launch.")
            return
        mod_name = self.mod_listbox.get(selection[0])
        working_dir = setup_mod_environment(mod_name)
        if working_dir:
            launch_game(working_dir)
        else:
            messagebox.showerror("Error", "Failed to set up mod environment.")

if __name__ == "__main__":
    app = LauncherGUI()
    app.mainloop()
