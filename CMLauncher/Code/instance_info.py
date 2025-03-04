import json
import os

from config import LOCAL_INSTANCE, LOCAL_VERSION


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
            return {"instance": LOCAL_INSTANCE, "version": LOCAL_VERSION, "last_played": ""}
    else:
        return {"instance": LOCAL_INSTANCE, "version": LOCAL_VERSION, "last_played": ""}


def write_global_instance_info(game, info):
    """Write Global Instance metadata to a file."""
    info_file = os.path.join(game["INSTANCES_DIR"], "Global_Instance_Info.json")
    with open(info_file, "w") as f:
        json.dump(info, f)