There is nothing to read here now hehe

## Setup
Requires Python 3 with tkinter (Windows: included with the python.org installer. Homebrew Python on Mac: `brew install python-tk@3.14`, matching your Python version).

Install the other dependencies once:

    Mac:      python3 -m pip install -r requirements.txt
    Windows:  py -m pip install -r requirements.txt

Blocking sites edits the hosts file, so it needs admin rights. Blocking apps works without them.

Run normally (apps only):

    Mac:      python3 main.py
    Windows:  py main.py

Run with admin rights (sites and apps):

    Mac:      sudo $(which python3) main.py
    Windows:  open the terminal with "Run as administrator", then: py main.py
