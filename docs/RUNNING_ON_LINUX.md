# Running MMV on Linux

Ubuntu was the easiest one to get it up and running, a little bit less trouble compared to Fedora but nothing too major. OpenSUSE was straightforward and included the most complete package list out of the box but don't this as the absolute word here.

As long as you have a working Python + dependencies, FFmpeg binaries and a OpenGL capable GPU or can make a GLFW context on the CPU you should be ok running this.

Also install optional dependency `mpv` for a post processing interface.

<hr>
<p align="center">
  <b>Instructions for each distro I tested</b>
</p>
<hr>

- **Arch Linux, Manjaro**: *Manjaro was tested on a clean install as of nov/2020, Arch Linux is the system I develop this on*
  - Python 3.9: `sudo pacman -Syu python python-setuptools python-pip base-devel ffmpeg git`

  - Python 3.8 (recommended): `sudo pacman -Syu python38 ffmpeg git`
  
  - (optional) `sudo pacman -Syu mpv`

<p>

- **Ubuntu**: *Tested on Ubuntu 20.04 minimal clean installation as of nov/2020*

  - `sudo apt update && sudo apt upgrade`

  - `sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev build-essential` 

  - (optional) `sudo apt install mpv`
<p>

- **Fedora**: *Tested on Fedora Workstation 33 clean installation as of nov/2020*

  - Enable the free rpmfusion repository for ffmpeg:
    - `sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm`

  - `sudo dnf upgrade`

  - `sudo dnf install python-devel ffmpeg git blas openblas lapack atlas libgfortran atlas-devel gcc-c++ gcc-gfortran subversion redhat-rpm-config python38` 

  - (optional) `sudo dnf install mpv`

<p>

- **OpenSUSE**: *Tested on OpenSUSE Tumbleweed rolling clean installation as of nov/2020 with free and non free repos configured*

  - `sudo zypper install git ffmpeg` (it already came with Python 3.8 and lapack / openblas shenanigans)
  
  - (optional) `sudo zypper install mpv`

<hr>

Open a shell on a directory and clone the repo:

- `cd ~` (In this example we'll clone mmv into `/home/USER/modular-music-visualizer`)

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/src`

<hr>
<p align="center">
  <b>Extra steps depending on your distro if any</b>
</p>
<hr>

##### Extra steps for Ubuntu, Fedora, OpenSUSE:

Replace `python` with `python3` on the following commands or have `alias python=python3` in your `~/.bashrc`)

##### Extra steps for Fedora / OpenSUSE:

Also before continuing, run `python3.8 -m ensurepip` otherwise it'll fail and not find `pip` for Python 3.8.

<hr>

### Continuing..

Preferably use a virtual environment:

- `python -m venv mmv-venv` (create the venv)

- `source ./mmv-venv/bin/activate` (activate the venv)

Then run `python base_video.py --auto-deps`

It should install Python dependencies automatically, if not run `pip install -r ./mmv/requirements.txt`

MMV should then run and generate the default video with default preset under the `renders` directory.

You can also run with `python base_video.py mode=[music,piano]` for quickly changing between the two. (mode=music is already implied if no argument is given)

Can also configure first then run `python post_processing.py` for applying some shaders to the output (mpv dependency required)

Head back to the original [RUNNING.md](RUNNING.md) for instructions on configuring your own stuff