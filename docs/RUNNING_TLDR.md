# Talk is cheap, show me the code!!

**Windows Note:** Pathing here uses the backslash instead of the traditional slash (use `\\`, not `/`)

- `yay -Syu ffmpeg python38 mpv musescore` (Arch Linux)

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/src`

(the next python commands might change on your distro / OS, try one of `python3.8` `python38` or on Windows `python.exe`)

- `python3.8 -m venv mmv-venv`

- `source ./mmv-venv/bin/activate`

- `pip install -r ./mmv/requirements.txt` (or run next step with `--auto-deps` flag)

- `python ./base_video.py` (music bars)

- `python ./base_video.py mode=piano` (piano roll)
  
- `python ./post_processing.py` (edit the file first with your config / what want to apply, can only render to video on Linux, viewing realtime works on any platform)

Final video will be located at `/src/renders` and where you configured your post processing output.
  
**Windows:** You'll need to install Python from [Python dot org](https://www.python.org/downloads/windows/) (please use Python 3.8) or using the `chocolatey` package manager (I never used that don't guarantee it working)

**MacOS** maybe `brew install brew install ffmpeg python mpv`
