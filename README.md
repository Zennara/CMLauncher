
# CMLauncher
![Discord](https://img.shields.io/discord/566984586618470411?label=discord)
![GitHub License](https://img.shields.io/github/license/zennara/CMLauncher)
![GitHub Release](https://img.shields.io/github/v/release/zennara/CMLauncher)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/zennara/CMLauncher/total)


A custom launcher for various games in the CastleMiner series that allows you to create seperate instances of the game for modded clients, or historical versions.


## Installation

1. Install the latest [release](https://github.com/Zennara/CMLauncher/releases).
2. Unzip the folder to your desired folder.
3. Start the launcher by running `CMLauncher.bat`.
4. Python will be prompted to install if it is not already.

### Alternate Installation
1. Install the lates release and unzip to desired folder.
2. Install [Python](https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe). Ensure to add the environment var to path:
3. Run `main.py` with Python either by opening it with your install `python.exe` or from the terminal.

    ![{82BC75E3-F1AC-4944-82D8-23201C9543E0}](https://github.com/user-attachments/assets/f0a7d235-eac4-44b8-852a-97f96a7da8ac)
    
## Terminology

### Versions
Verions are complete, full versions of the CM game and all of its required files. Your Steam Version is your currently installed Steam version of the game. This *can* change if you directly modify your game files without use of this launcher.

### Instances
Instances are created from versions. After creation, and instance's files can be edited (mods can be installed, as well) without affecting its associated Version.
## Usage

### First Launch
On your first lanch of CMLauncher, the launcher will attempt to located your CM game directories automatically. If it fails, you will need to set up the installation path for each game manually on its respective tab.

### General
Modify your existing Versions/Instances or create new ones by clicking their respective buttons. From there, you can right click to perform specific functions on them.

### Installing Mods
To install a modded version to a launcher version follow these steps:
1. Create the appropriate base game Version for the modded client, if you have not already.
2. Create a new Intance for your mod, if you do not have one already. *Tip: You can create new Instances for each mod version.*
3. Open the folder location for your created Instance.
4. Copy and replace all of the mods files (or follow mod-specific installation instructions)
5. Select the instance, and play!
## Contributing

Contributions are always welcome!

See [contributing.md](https://github.com/Zennara/CMLauncher/blob/main/CONTRIBUTING.md) for ways to get started.

Please adhere to this project's [code of conduct](https://github.com/Zennara/CMLauncher?tab=coc-ov-file).

