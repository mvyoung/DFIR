# cx_Freeze is required to bundle into an exe
# Run pip install cx_Freeze" to install
# Run "python setup.py build" to create build/ with the .exe and all dependencies included

import sys
from cx_Freeze import setup, Executable

base = None

executables = [Executable("welcome_commander.py", base=base)]

packages = []
options = {
   'build_exe': {
      'packages':packages,
   },
}

setup(
   name = "DFIR",
   #options = options,
   version = "0.1",
   description = "suite of DFIR tools",
   executables = executables
)