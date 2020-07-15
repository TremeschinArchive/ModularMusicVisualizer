# Modular Music Visualizer

An attempt to make a free (as in freedom) and open source music visualization software

![Demo image of MMV](repo/demo.jpg)

[Link to unlisted video of the full music in the image above](https://youtu.be/BhpLwaR1Oj8)

# Running

## Windows

I have tried running it under Windows, I reverted the ray multiprocessing library I was using because it wasn't working and still under alpha stages on this OS to Python's default multiprocessing library.

However I think that cairosvg requires the Visual Studio Build Tools thingy, so grab that before installing Python dependencies.

Go ahead to [python.org](https://www.python.org/) and install Python 3.8, be sure to check the box to add Python to the PATH variable on the installer.

Download the source code on the repo main page or clone the repo with `git clone https://github.com/Tremeschin/modular-music-visualizer`

Preferably [Use a Python venv](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs), not required but optimal

Now open a shell (shift + right click empty spot on the Windows folder manager, open PowerShell), run `pip install -r mmv/requirements.txt` to install Python dependencies

#### I'd like some feedback if you could install everything fine and what you had to do to make it work :)

Configure the stuff on the file `example.py`, run it with `python example.py`

I include a few free assets under the `assets/free_assets` folder, you can use them at your disposal :)

## Linux

`git clone https://github.com/Tremeschin/modular-music-visualizer`

`cd modular-music-visualizer/src`

[Use a Python venv](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs) (recommended):

- `python -m venv mmv-venv`

- `source ./mmv-venv/bin/activate`

`pip install -r mmv/requirements.txt`

Configure the stuff on the file `example.py`, run it with `python example.py`

I include a few free assets under the `assets/free_assets` folder, you can use them at your disposal :)

# Wiki is TODO
