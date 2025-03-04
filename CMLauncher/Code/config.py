# Set BASE_DIR to the folder where this script is located.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL_PATHS_FILE = os.path.join(BASE_DIR, "install_paths.json")

LOCAL_VERSION = "Steam Version"
LOCAL_INSTANCE = "Global Instance"

VERSION = "1.0.0"

BASE_ICON = os.path.join(BASE_DIR, r"Code\assets\icon.ico")
MANAGE_ICON = os.path.join(BASE_DIR, r"Code\assets\manage.ico")
PLUS_ICON = os.path.join(BASE_DIR, r"Code\assets\plus.ico")
QUESTION_ICON = os.path.join(BASE_DIR, r"Code\assets\question.ico")
EXCLAMATION_ICON = os.path.join(BASE_DIR, r"Code\assets\exclamation.ico")
ERROR_ICON = os.path.join(BASE_DIR, r"Code\assets\error.ico")

# Define game configurations. Folders will be under CMLauncher/<GameName>/...
games = {
    "CastleMiner Z": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Games", "CastleMiner Z", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Games", "CastleMiner Z", "Instances"),
        "APP_ID": 253430,
        "EXE_NAME": "CastleMinerZ.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Z",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Z"
        ]
    },
    "CastleMiner Warfare": {
        "VERSIONS_DIR": os.path.join(BASE_DIR, "Games", "CastleMiner Warfare", "Versions"),
        "INSTANCES_DIR": os.path.join(BASE_DIR, "Games", "CastleMiner Warfare", "Instances"),
        "APP_ID": 675210,
        "EXE_NAME": "CastleMinerWarfare.exe",
        "POSSIBLE_PATHS": [
            r"C:\Program Files (x86)\Steam\steamapps\common\CastleMiner Warfare",
            r"C:\Program Files\Steam\steamapps\common\CastleMiner Warfare"
        ]
    }
}