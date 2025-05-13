# Team Members
1. Grant Roach (Team Lead)
2. Austin Devito-Spiro
3. Tripp Skaggs
4. Joseph Johnson
5. Braeden McGarvey
_________________
## Hardware Requirements
* A Windows Based System with a Multi-Core Processor
* Ideally a System with a Dedicated Graphics Card to handle processing
_________________
## Necessary Components
* **A Chessboard** - 7x7 is ideal, no smaller. Bigger is allowed with varying results.
* **A Camera** - We have found that this works best with an external camera that is moveable rather than a Laptop Webcam, which may detect at an angle that renders board detection impossible with pieces on the board. 
* **Chess Pieces** - Currently Chess Pieces are the objects we are using for our Towers/Defenders. We have found that the model detecting the pieces has an easier time detecting the Lighter Color chess pieces of the set. Chess Pieces that are outside of standard styling may be detected with varying results.
_________________
## How To Install:
### (Note: We have found that this program does not run on ARM based Mac's. There seems to be an issue or error with Threading and OpenCV at this time.)

1. If you do not have .venv installed, first create the virtual environment locally by running: **python -m venv venv**

2. After this is done, you need to activate the virtual environment. You can do this with the command: **venv\Scripts\activate**

You will know that it is activated because you'll see the (venv) tag show up in your terminal. Virtual environments are a way to install and manage dependencies on a per-project basis instead of installing the modules globally.

3. You can install dependencies one of two ways. The easiest is to have a requirements.txt file available. Just run the command: **pip install -r requirements.txt**

4. Once you have the requirements installed, you will need to have a camera connected to the system running the game (While not fully required it is the intended way of play, otherwise a provided JSON file may be used to play, the JSON file must be named "detected_pieces.json"). The Camera ideally should be set in either a Top-Down configuration or off to one of the sides and angled so that the camera can see the whole Chess Board. 

5. The object and board detection script launches at the same time as the main TowerDefense script, which can be ran through terminal with **python TowerDefense.py**

6. Place pieces on the board before starting the game to gather a grasp of where the pieces will be rendered. 

7. Press the **R** key on your keyboard to recalibrate the chessboard grid detection

8. The game and subsequent rounds may be started with the **SPACE** button. 

9. During the prep phase which happens between each round you are allowed to place one more piece on the board. 