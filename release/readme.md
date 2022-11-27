# About
Bitboxing is a modern, digital scavenger hunt that utilizes Quick Response (QR)
codes. In the game of Bitboxing, QR codes are hidden around the play area.
Players search for and scan each QR code to see puzzles to solve. The prototype
version of Bitboxing comes with five QR codes with corresponding puzzles.

Bitboxing is written in Python 3 using the built-in Tkinter, Socket, and SQLite3
libraries. Bitboxing comes with both graphical user interface (GUI) and
command-line interface (CLI) client applications. The GUI application uitilizes
the third-party libaries Pillow, OpenCV, and pyzbar.

# Getting Started
1. Install [Python 3](https://www.python.org/downloads/)
2. Install dependencies:
- [Pillow](https://pillow.readthedocs.io/en/stable/)
- [OpenCV](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [pyzbar](https://pypi.org/project/pyzbar/)
3. Configure your desired server IP address and port number in
   bitboxing_server.py, bitboxing_cli.py, and bitboxing_gui.py.
4. Run bitboxing_server.py to launch the server on your host device.
5. Have players run a client application on their devices:
- Command-Line Interface: bitboxing_cli.py
- Graphical User Interface: bitboxing_gui.py

# Playing Bitboxing
1. Print out QR codes and place them around your play area in hidden locations.
2. Have players scan any QR codes they find with the Bitboxing GUI application
   or any QR code scanner.
3. If players scan using the Bitboxing GUI application, they will automatically
   be taken a screen where they can try to solve the scanned QR code's puzzle.
   If players are using the command-line interface, they can type the code that
   is displayed by their QR code scanner.
4. Try to solve as many puzzles as you can as quickly as you can!
5. Check the game leaderboard and the leaderboards for each puzzle to compare
   your progress with old and new players.