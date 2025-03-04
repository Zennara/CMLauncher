import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

# Set BASE_DIR to the folder where this script is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Updated folder names:
GAME_CACHE = os.path.join(BASE_DIR, "Launcher/GameCache")      # Full base game cache
VERSIONS_DIR = os.path.join(BASE_DIR, "Launcher/Versions")       # Version files (only changes)
INSTANCES_DIR = os.path.join(BASE_DIR, "Launcher/Instances")     # Persistent instance folders

# The default install path will be auto-detected.
BASE_GAME_PATH = None  # We'll set this during initial setup.
VANILLA_VERSION = "Vanilla 1.9.8.0"


def ensure_folders():
    """Ensure that necessary folders exist."""
    for folder in [VERSIONS_DIR, INSTANCES_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"[INFO] Created folder: {folder}")


def cache_base_game(base_game_path):
    """Cache the base game if it's not cached already."""
    if not os.path.exists(GAME_CACHE):
        print("[INFO] Caching base game from:", base_game_path)
        shutil.copytree(base_game_path, GAME_CACHE)
    else:
        print("[INFO] Base game already cached.")


def find_castleminerz_install():
    """
    Try to auto-detect the CastleMiner Z install location by checking common Steam paths.
    """
    possible_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
        r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
    ]
    for path in possible_paths:
        if os.path.exists(os.path.join(path, "CastleMinerZ.exe")):
            return path
    return None


def auto_detect_install_location():
    """
    Attempt to auto-detect the CastleMiner Z installation location.
    If found, ask the user to confirm.
    If not, prompt the user to input it manually.
    """
    install_path = find_castleminerz_install()
    if install_path:
        if messagebox.askyesno("Confirm Install Location",
                               f"Detected CastleMiner Z installation at:\n{install_path}\nIs this correct?"):
            return install_path
    # If auto-detection fails or user says no, ask for manual entry.
    manual_path = simpledialog.askstring("Install Location",
                                           "Enter the full path to your CastleMiner Z installation:")
    return manual_path


def overlay_version_files(instance_path, version):
    """
    Overlay version-specific files onto an instance folder.
    If version is VANILLA_VERSION, nothing extra is done.
    Otherwise, files from the Versions folder are overlaid.
    """
    if version == VANILLA_VERSION:
        return

    version_path = os.path.join(VERSIONS_DIR, version)
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


def create_instance(instance_name, version):
    """
    Create a new instance with the given name and version.
    The instance is created by copying the GAME_CACHE folder,
    then overlaying version-specific files if needed.
    """
    instance_path = os.path.join(INSTANCES_DIR, instance_name)
    if os.path.exists(instance_path):
        messagebox.showerror("Error", f"An instance named '{instance_name}' already exists!")
        return None

    try:
        print(f"[INFO] Creating new instance '{instance_name}' with version '{version}'...")
        shutil.copytree(GAME_CACHE, instance_path)
        overlay_version_files(instance_path, version)
        return instance_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create instance: {e}")
        return None


def launch_game(instance_path):
    """Launch CastleMiner Z from the given instance folder with steam_appid.txt."""
    game_exe = os.path.join(instance_path, "CastleMinerZ.exe")
    app_id_path = os.path.join(instance_path, "steam_appid.txt")

    # Ensure steam_appid.txt exists
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
    """Open the given instance folder in Windows Explorer."""
    if os.path.exists(instance_path):
        subprocess.Popen(["explorer", instance_path])
    else:
        messagebox.showerror("Error", "Instance folder not found.")


def delete_instance(instance_path):
    """Delete the given instance folder after user confirmation."""
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this instance?"):
        try:
            shutil.rmtree(instance_path)
            messagebox.showinfo("Deleted", "Instance deleted successfully.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete instance: {e}")
    return False


def list_instances():
    """List all instance folders from INSTANCES_DIR."""
    if not os.path.exists(INSTANCES_DIR):
        os.makedirs(INSTANCES_DIR)
    return [instance for instance in os.listdir(INSTANCES_DIR)
            if os.path.isdir(os.path.join(INSTANCES_DIR, instance))]


def get_version_options():
    """
    Return a list of available versions.
    Always include VANILLA_VERSION, then any folders found in VERSIONS_DIR.
    """
    options = [VANILLA_VERSION]
    if os.path.exists(VERSIONS_DIR):
        for folder in os.listdir(VERSIONS_DIR):
            folder_path = os.path.join(VERSIONS_DIR, folder)
            if os.path.isdir(folder_path):
                options.append(folder)
    return options


def new_instance_dialog(master):
    """
    Open a dialog that prompts the user for a new instance name and version.
    If confirmed, create the instance and update the instance list.
    """
    dialog = tk.Toplevel(master)
    dialog.title("Create New Instance")
    dialog.geometry("300x200")

    tk.Label(dialog, text="Instance Name:").pack(pady=5)
    name_entry = tk.Entry(dialog)
    name_entry.pack(pady=5)

    tk.Label(dialog, text="Version:").pack(pady=5)
    version_options = get_version_options()
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
        instance_path = create_instance(instance_name, version)
        if instance_path:
            messagebox.showinfo("Success", f"Instance '{instance_name}' created.")
            master.populate_instances()
            dialog.destroy()

    create_button = tk.Button(dialog, text="Create Instance", command=on_create)
    create_button.pack(pady=10)


class LauncherGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMLauncher")
        self.geometry("500x500")
        self.create_widgets()
        self.populate_instances()
        cache_base_game(BASE_GAME_PATH)

    def create_widgets(self):
        # --- Instance Manager Section ---
        header = tk.Label(self, text="Instances", font=("Arial", 14))
        header.pack(pady=10)

        self.instance_listbox = tk.Listbox(self, height=12)
        self.instance_listbox.pack(fill=tk.BOTH, expand=True, padx=20)
        self.instance_listbox.bind("<<ListboxSelect>>", self.on_instance_select)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=10)

        # "New Instance" button always visible
        new_instance_button = tk.Button(self.buttons_frame, text="New Instance",
                                        command=lambda: new_instance_dialog(self))
        new_instance_button.grid(row=0, column=0, padx=5)

        # The following buttons are only enabled when an instance is selected.
        self.start_button = tk.Button(self.buttons_frame, text="Start", command=self.start_instance, state=tk.DISABLED)
        self.start_button.grid(row=0, column=1, padx=5)

        self.open_button = tk.Button(self.buttons_frame, text="Open Folder", command=self.open_instance,
                                     state=tk.DISABLED)
        self.open_button.grid(row=0, column=2, padx=5)

        self.delete_button = tk.Button(self.buttons_frame, text="Delete", command=self.delete_instance,
                                       state=tk.DISABLED)
        self.delete_button.grid(row=0, column=3, padx=5)

    def populate_instances(self):
        self.instance_listbox.delete(0, tk.END)
        for instance in list_instances():
            self.instance_listbox.insert(tk.END, instance)
        self.set_action_buttons_state(False)

    def on_instance_select(self, event):
        selection = self.instance_listbox.curselection()
        if selection:
            self.set_action_buttons_state(True)
        else:
            self.set_action_buttons_state(False)

    def set_action_buttons_state(self, state):
        new_state = tk.NORMAL if state else tk.DISABLED
        self.start_button.config(state=new_state)
        self.open_button.config(state=new_state)
        self.delete_button.config(state=new_state)

    def get_selected_instance_path(self):
        selection = self.instance_listbox.curselection()
        if selection:
            instance_name = self.instance_listbox.get(selection[0])
            return os.path.join(INSTANCES_DIR, instance_name)
        return None

    def start_instance(self):
        instance_path = self.get_selected_instance_path()
        if instance_path:
            launch_game(instance_path)

    def open_instance(self):
        instance_path = self.get_selected_instance_path()
        if instance_path:
            open_instance_folder(instance_path)

    def delete_instance(self):
        instance_path = self.get_selected_instance_path()
        if instance_path:
            if delete_instance(instance_path):
                self.populate_instances()


def initial_setup():
    """Perform initial setup: create required folders and determine the install location."""
    ensure_folders()
    global BASE_GAME_PATH
    # If GameCache is not cached yet, try to auto-detect CastleMiner Z install location.
    if not os.path.exists(GAME_CACHE):
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the temporary window.
        detected_path = auto_detect_install_location()
        temp_root.destroy()
        if detected_path is None or not os.path.exists(os.path.join(detected_path, "CastleMinerZ.exe")):
            messagebox.showerror("Error", "Invalid CastleMiner Z install location. Exiting.")
            exit(1)
        BASE_GAME_PATH = detected_path
        # Prompt to verify integrity (cache the base game).
        if messagebox.askyesno("Verify Files", "Do you want to cache the base game files from the detected installation?"):
            cache_base_game(BASE_GAME_PATH)
        else:
            messagebox.showerror("Error", "Base game not cached. Exiting.")
            exit(1)
    else:
        # If already cached, use the existing BASE_GAME_PATH (could be stored in a config file).
        # For simplicity, we keep BASE_GAME_PATH unchanged.
        pass


if __name__ == "__main__":
    initial_setup()
    app = LauncherGUI()
    app.mainloop()
