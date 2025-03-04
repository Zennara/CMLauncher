import os
import shutil
import subprocess

# Paths (customize these to your setup)
BASE_DIR = r"C:\Users\Keagan\Desktop\CMLauncher"
GAME_CACHE = os.path.join(BASE_DIR, "GameCache")       # Full base game cache
MODS_DIR = os.path.join(BASE_DIR, "Mods")              # Mod files (only changes)
WORKING_DIRS = os.path.join(BASE_DIR, "WorkingDirs")   # Isolated environments

def cache_base_game(base_game_path):
    """ Cache the base game if it's not cached already """
    if not os.path.exists(GAME_CACHE):
        print("[INFO] Caching base game...")
        shutil.copytree(base_game_path, GAME_CACHE)
    else:
        print("[INFO] Base game already cached.")

def setup_mod_environment(mod_name):
    """ Create an isolated working directory for the selected mod """
    mod_path = os.path.join(MODS_DIR, mod_name)
    mod_working_dir = os.path.join(WORKING_DIRS, mod_name)

    if not os.path.exists(mod_path):
        print(f"[ERROR] Mod '{mod_name}' not found!")
        return None

    # Ensure clean working directory
    if os.path.exists(mod_working_dir):
        shutil.rmtree(mod_working_dir)

    # Copy cached base game
    print(f"[INFO] Setting up isolated environment for '{mod_name}'...")
    shutil.copytree(GAME_CACHE, mod_working_dir)

    # Overlay mod-specific files
    for root, _, files in os.walk(mod_path):
        for file in files:
            relative_path = os.path.relpath(root, mod_path)
            dest_path = os.path.join(mod_working_dir, relative_path, file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(os.path.join(root, file), dest_path)

    return mod_working_dir

def launch_game(working_dir):
    """ Launch CastleMiner Z from the isolated working directory with steam_appid.txt. """
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

        subprocess.run(game_exe, cwd=working_dir, env=env)
    else:
        print("[ERROR] Game executable not found!")



def list_mods():
    """ List available mods """
    return [mod for mod in os.listdir(MODS_DIR) if os.path.isdir(os.path.join(MODS_DIR, mod))]

if __name__ == "__main__":
    # Step 1: Cache the base game (if needed)
    base_game_path = r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z"
    cache_base_game(base_game_path)

    # Step 2: Display available mods
    print("Available Mods:")
    mods = list_mods()
    for mod in mods:
        print(f" - {mod}")

    # Step 3: Select and launch a mod
    mod_name = input("Enter the mod to launch: ").strip()
    if mod_name in mods:
        working_dir = setup_mod_environment(mod_name)
        if working_dir:
            launch_game(working_dir)
    else:
        print("[ERROR] Invalid mod selection.")
