# Modular Music Visualizer

An attempt to make a music visualization software

Only basic stuff work yet :p , hello if you're here before everything :p

# Running

Only works on Linux at the time

`git clone https://github.com/Tremeschin/modular-music-visualizer`

`cd modular-music-visualizer/src`

[Use a Python venv](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs) (recommended):

- `python -m venv mmv-venv`

- `source ./mmv-venv/bin/activate`

`pip install -r requirements.txt`

`python main.py -i [audio.extension]`

Configure the stuff under `mmvanimation.py` on function `generate` and follow the code flow
