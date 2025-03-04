# Set BASE_DIR to the folder where this script is located.
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALL_PATHS_FILE = os.path.join(BASE_DIR, "install_paths.json")

LOCAL_VERSION = "Steam Version"
LOCAL_INSTANCE = "Global Instance"

BASE_ICON = "assets/icon.ico"
MANAGE_ICON = "assets/manage.ico"
PLUS_ICON = "assets/plus.ico"
QUESTION_ICON = "assets/question.ico"
EXCLAMATION_ICON = "assets/exclamation.ico"
ERROR_ICON = "assets/error.ico"

# Define game configurations. Folders will be under Launcher/<GameName>/...
games = {
    "CastleMiner Z": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "CMLauncher", "CastleMiner Z", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "CMLauncher", "CastleMiner Z", "Instances"),
        "APP_ID": 253430,
        "EXE_NAME": "CastleMinerZ.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
        ]
    },
    "CastleMiner Warfare": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "CMLauncher", "CastleMiner Warfare", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "CMLauncher", "CastleMiner Warfare", "Instances"),
        "APP_ID": 675210,
        "EXE_NAME": "CastleMinerWarfare.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Warfare",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Warfare"
        ]
    }
}