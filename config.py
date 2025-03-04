# Set BASE_DIR to the folder where this script is located.
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_VERSION = "Steam Version"
LOCAL_INSTANCE = "Global Instance"

# Define game configurations. Folders will be under Launcher/<GameName>/...
games = {
    "CastleMiner Z": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Z", "Instances"),
        "EXE_NAME": "CastleMinerZ.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
        ]
    },
    "CastleMiner Warfare": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Launcher", "CastleMiner Warfare", "Instances"),
        "EXE_NAME": "CastleMinerWarfare.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Warfare",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Warfare"
        ]
    }
}