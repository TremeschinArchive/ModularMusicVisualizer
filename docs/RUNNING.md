
**TL;DR:* If you think talk is cheap and show me the code, see [RUNNING_TLDR.md](RUNNING_TLDR.md)

## IMPORTANT!!

### YOU MUST USE A 64 BIT PYTHON INSTALLATION

`skia-python` package only includes 64 bit wheels on PyPI as Skia 32 bits is not available for the public.

The code will check itself for a 64 bit installation and quit if this is not met.

<hr>

### Python 3.9 is acting weird

Please try using Python version 3.8 when running MMV, I'm having lots of troubles with 3.9 dependencies (namely `scikit-learn` plus numpy and llvmlite aka the three musketeers)

So look for Python version 3.8 on your distro / MacOS homebrew / when downloading from pythong dot org on Windows, you'd probably want to use `python38` or `python3.8` binary instead of just `python` or `python3`.

<hr>

### The "versions" of MMV

- **MMVSkia**
  - "Old" code (first iteration of it).
  - Piano roll mode
  - Music Bars mode
  - Uses Skia as drawing backend
  - Should work on every platform
  - Quite slow if using video as background or 1080p+ resolutions
  - Files `/src/base_video.py` and `/src/piano_roll.py`
  - Music bars mode *can be deprecated* in favor of MMVShaderMGL in the long term but not Piano Roll.

- **MMVShaderMGL**
  - Heavily *WIP*
  - Uses Python's `moderngl` package:
    - Renders a single GLSL Shader file to a video
  - Can map videos, images and other shaders as textures (layers)
  - Stupidly fast, real time + performance
  - Astronomically more possibilities relative to MMVSkia
  - Needs lot of work to be done or even usable
  - File `/src/mmv/test_mgl.py`

- **MMVShaderMPV**
  - Uses the MPV video player
  - Applies MPV syntax specific shaders to video real time
  - Only works on Linux rendering to a video file, others can visualize
  - Was experimental when I was R&D, probably will be removed soon

# Running

## External dependencies

If you're on Windows the code should (hopefully) take care of the external dependencies.

Both MMVSkia and MMVShaderMGL will require FFmpeg for encoding the final video.

MMVSkia Piano roll optional dependency is `musescore` for converting the MIDI file to an audio file automatically, you can set this up manually otherwise (your own source audio for the midi file).

MMVShaderMPV will require `mpv` as an external dependency.

If you're on macOS and Linux, you'll need to install the `mpv, musescore, ffmpeg` on your distro package manager / homebrew on macOS. It's better to do so as they'll download the latest one and be available on PATH immediately.

<hr>

## Linux

Install from your distro package manager:

- `git ffmpeg python38 musescore`

_(musescore is optional)_

Also please have the corresponding graphics driver package for your GPU, I run MMV with `mesa` (AMD and Intel GPUs), while NVIDIA GPUs will require the `nvidia-drivers`, though out of the scope to get them running.

Don't know if Noveau drivers will work with NVIDIA nor AMDGPU pro use at your own risk.
  
Few examples:

- **Arch Linux, Manjaro:**
  - `$ sudo pacman -Syu base-devel git ffmpeg python38 musescore`
- **Ubuntu**:
  - `$ sudo apt update && sudo apt upgrade`
  - `$ sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev build-essential`
- **Fedora**:
  - Enable repo for FFmpeg: 
    - `$ sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm`
  - `$ sudo dnf upgrade`
  - `$ sudo dnf install python-devel ffmpeg git blas openblas lapack atlas libgfortran atlas-devel gcc-c++ gcc-gfortran subversion redhat-rpm-config python38 musescore`
- **OpenSUSE**:
  - `$sudo zypper install git ffmpeg musescore` (it already came with Python 3.8 and lapack / openblas shenanigans)

Feel free to open issue for bad usage of these package managers or steps for some other distro, I can't know 'em all

<hr>

Open a shell on a directory, clone the repo and install dependencies:

- `$ git clone https://github.com/Tremeschin/modular-music-visualizer`
- `$ cd ./modular-music-visualizer/src/`

It's not bad to create a virtual environment for isolating the Python packages:

- `$ python3.8 -m venv mmv_python_virtualenv`
- `$ source ./mmv_python_virtualenv/bin/activate` (always source this before using MMV)

- `$ python3.8 -m pip install -r ./mmv/requirements.txt`

Depending on which distro you are `python3.8` can be called `python38`, just type `python` and tab through the results.

You might want also to run:

- `$ python3.8 -m ensurepip`

If this fails then you might want to install the corresponding Python setup tools package.


- Edit these scripts (or don't for the default demo config and audio) and run MMV with:
  - `$ python3.8 ./base_video.py`
  - `$ python3.8 ./piano_roll.py`

<hr>

## MacOS

Open a terminal on a directory you want to download and execute MMV. 

- Install Python and dependencies with:
  - `$ brew install python@3.8 ffmpeg musescore git`
- Clone the source code:
  - `$ git clone https://github.com/Tremeschin/modular-music-visualizer`
- Change the working directory:
  - `$ cd ./modular-music-visualizer/src/`

It's not bad to create a virtual environment for isolating the Python packages:

- `$ python3.8 -m venv mmv_python_virtualenv`
- `$ source ./mmv_python_virtualenv/bin/activate` (always source this before using MMV)
  
- Install Python requirements:
  - `$ python3.8 -m pip install -r ./mmv/requirements.txt`
- Edit these scripts (or don't for the default demo config and audio) and run MMV with:
  - `$ python3.8 ./base_video.py`
  - `$ python3.8 ./piano_roll.py`

<hr>

## Windows

Download the source code of the project on the main repository page, should be a button with an arrow pointing down, otherwise install Git CLI and open a shell on some directory, run `git clone https://github.com/Tremeschin/modular-music-visualizer`

There is two .bat scripts I wrote located at `/src/bootstrap/{install_python,install_dependencies}.bat`, I don't guarantee them to work but you should be good to go by running those.

Shift right click inside that bootstrap folder, click `Open PowerShell` here, you can them execute those scripts by typing `.\install_python.bat` and pressing enter then `.\install_dependencies.bat`.

After that either type `cd ..` or open another shell into the `/src/` dir, you should be able to run MMV with:

- `python38.exe ./base_video.py`
- `python38.exe ./piano_roll.py`

If this fails then just read the Linux instructions and follow along on the section after some demo commands for some distributions, of course searching for how to do that on Windows.

<hr>

# Editing configs

If you're going to venture out on creating your own MMV scripts or hacking the code, making new presets, I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfalls.

Otherwise just read through the example scripts for stuff you can do, it's hard to micro manage everything.
