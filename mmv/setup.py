from cx_Freeze import setup, Executable

base = None    

executables = [Executable("example_basic.py", base = base)]

packages = ["pyunpack", "numpy", "llvmlite"]

options = {
    'build_exe': {    
        'packages': packages,
    },    
}

setup(
    name = "Modular Music Visualizer",
    options = options,
    version = "2.3.5",
    description = 'After Effects-like music visualization and Piano Rolls!!',
    executables = executables
)
