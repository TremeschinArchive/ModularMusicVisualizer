from cx_Freeze import setup, Executable
from setuptools import find_packages
import sys
import os

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_FILE_DIR)

found = find_packages(THIS_FILE_DIR)
print("Found packages", found)

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable(f"{THIS_FILE_DIR}/example_basic.py", base = base)]

packages = ["pyunpack", "numpy", "llvmlite", "mmv"]

options = {
    'build_exe': {    
        'packages': packages,
        "optimize": 2,
        "bin_includes": f"{THIS_FILE_DIR}/mmv/externals/ffmpeg.exe"
    },    
}

setup(
    name = "Modular Music Visualizer",
    options = options,
    version = "2.3.5",
    description = 'After Effects-like music visualization and Piano Rolls!!',
    executables = executables
)
