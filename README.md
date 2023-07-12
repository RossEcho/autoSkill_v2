# autoSkill_v2
Auto Key Presser for Diablo IV
Description
This is a Python script that automates key pressing and healing for the game Diablo IV.

The first part of the script presses a set of keys at specified intervals. This is useful for automatically using skills that have cooldowns.

The second part monitors the player's health and automatically presses a healing key when the health drops below a certain threshold. This is achieved by comparing the current health bar to an image of an empty health bar.

The script uses Tkinter for the GUI, OpenCV for image comparison, PyAutoGUI for capturing screenshots and simulating key presses, and keyboard for registering hotkeys.

Installation
Clone this repository or download the code as a ZIP file and extract it.
Install the necessary Python libraries with the following command: pip install -r requirements.txt

Usage
Run the script with Python autoSkill.py.
The GUI will appear. Enter the keys to be pressed and their frequencies, the key to be pressed for healing, and the threshold for health monitoring.
Click the 'Start' button to start the script. The keys will be pressed at the specified intervals.
If health monitoring is enabled, the script will start scanning the health bar and press the healing key when the health drops below the threshold. The threshold is a similarity percentage between the current health bar and an empty health bar. A lower threshold means the health bar must be closer to being empty before healing is triggered.

Configuration
The coordinates of the health bar in the game window and the path to the image of an empty health bar need to be set in the script.
The script currently supports 5 keys for skills and one key for healing. The number of skill keys can be adjusted in the script.
Screen resolution 1920*1080(16:9 Widescreen), HUD set to center.

Notes
The script was written for a specific game and may not work properly with other games or game settings. Adjustments may be needed to make it work with other games.
The script uses the similarity between the current health bar and an image of an empty health bar to determine when to press the healing key. Therefore, it may not work properly if the game's health bar design or color changes, or if there are other UI elements overlaying the health bar.

License
The code is licensed under the MIT License. See the LICENSE file for more details.
