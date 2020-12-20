# These are instructions for running the MMV with skia rendering backend on many platforms.

This is currently the only one fully working and functional MMV.

## IMPORTANT!!

<hr>

### YOU MUST USE A 64 BIT PYTHON INSTALLATION

`skia-python` package only includes 64 bit wheels on PyPI as Skia 32 bits is not available for the public.

The code will check itself for a 64 bit installation and quit if not.

<hr>

# Installing Python, FFmpeg and dependencies

Also see [EXTRAS.md](../docs/EXTRAS.md) file for squeezing some extra performance.

<hr>

## Linux:

Ubuntu was the easiest one to get it up and running, a little bit less trouble compared to Fedora but nothing too major. OpenSUSE was straightforward and included the most complete package list out of the box.

As long as you have a working Python + dependencies, FFmpeg binaries and a OpenGL capable GPU or can make a GLFW context on the CPU you should be ok running this.

<hr>
<p align="center">
  <b>Instructions for each distro I tested</b>
</p>
<hr>

- **Arch Linux, Manjaro**: *Manjaro was tested on a clean install as of nov/2020, Arch Linux is the system I develop this on*
  - `sudo pacman -Syu python python-setuptools python-pip base-devel ffmpeg git`

<p>

- **Ubuntu**: *Tested on Ubuntu 20.04 minimal clean installation as of nov/2020*

  - `sudo apt update && sudo apt upgrade`

  - `sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev build-essential` 

<p>

- **Fedora**: *Tested on Fedora Workstation 33 clean installation as of nov/2020*

  - Enable the free rpmfusion repository for ffmpeg:
    - `sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm`

  - `sudo dnf upgrade`

  - `sudo dnf install python-devel ffmpeg git blas openblas lapack atlas libgfortran atlas-devel gcc-c++ gcc-gfortran subversion redhat-rpm-config python38` 

<p>

- **OpenSUSE**: *Tested on OpenSUSE Tumbleweed rolling clean installation as of nov/2020 with free and non free repos configured*

  - `sudo zypper install git ffmpeg` (it already came with Python 3.8 and lapack / openblas shenanigans)
  
<hr>

Open a shell on a directory and clone the repo:

- `cd ~` (In this example we'll clone mmv into `/home/USER/modular-music-visualizer`)

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/mmv`

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

Then run `python example_basic.py --auto-deps`

It should install Python dependencies automatically, if not run `pip install -r ./mmv/requirements.txt`

MMV should then run and generate the default video with default preset under the `renders` directory.

See after Windows section for info on configuring your own stuff or click [HERE](#editing-configs)

<hr>

## macOS // Help needed

I am very inexperienced with macOS but here's the steps I had to do for getting MMV up and *(half)* running:

- Install `homebrew`, I don't know how often people do this or even use it.. but it's a package manager and should make stuff easier.
  
  - Go to https://brew.sh/ and run their command on *"Install Homebrew"* section

  This should take a while since it requires that Xcode CLI thing where it is not small.

- After it's installed, run `brew install ffmpeg python` to install Python (3.8 was what I got) and FFmpeg (the video encoder)

I already had `git` so just do:

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/mmv`

Then run `python3 example_basic.py --auto-deps --user`

If you want it automatically to convert `MIDI -> audio` please also run `brew install fluidsynth --with-libsndfile`

I did get a few OpenGL errors when doing this as I was using a mac VM with the scripts of this repo: https://github.com/foxlet/macOS-Simple-KVM

**Disclaimer:** I just installed the system for testing my code, I won't use any products I don't own there, I just want to support many platforms as possible. This was the cheap and dirty solution of it I was sure I'd get a few errors there, but most stuff went fine.

Feedback wanted on native macOS, this is as far as I can help you for now. I can say one friend of mine could run and it worked, however he had to downgrade to Python 3.8 under homebrew.

See after Windows section for info on configuring your own stuff or click [HERE](#editing-configs)

<hr>

## Windows:

This project isn't extensively tested on Windows, feedback appreciated.

<hr>
<p align="center">
  <i>Prepare your disks and patience!!</i>
</p>
<hr>

Any easier steps for Windows are welcome specially for external installs other than Python that are needed.

**Chose:**

<hr>

##### 1. With Anaconda (less trouble)

Download and install `Anaconda` (not `miniconda`), make it your default Python optimally on the installer.

<hr>

##### 2. With vanilla Python (discouraged somehow)

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer).

You'll also need to download `Build Tools for Visual Studio` which got merged into Visual Studio Community Edition, so search that (Build Tools for VS) and download the installer of the VS Community.

You'll need to install the whole C++ development package group so Python can use a compiler and the Windows SDK for building dependencies such as numpy. This will use quite a bit of disk space and definitely will take a while to complete. After that you can proceed to the next steps.

Search for `scipy` Python wheels and install the version listed on `requirements.txt`.

For this last step you can also manage to install lapack or blas / openblas on your system. I could not. This is finicky and I offer no official support for this.

<hr>

### Important: extra step for an automatic installation of dependencies

Go to [7-zip downloads](https://www.7-zip.org/download.html) website, download the `7-Zip for 64-bit Windows x64 (Intel 64 or AMD64)` executable if you don't have it already installed, run it and extract the files on the default path.


This step is required to extract the video encoder (FFmpeg) compressed files if you don't want to do this by hand.

<hr>

### Getting the source code

<hr>

**Chose:**

#### 1. GitHub / GitLab repository main page

You might be already here, head to the top page and there is a (green for GitHub, blue for GitLab) button _"⬇️ Code"_ and download as a ZIP.

Use a archive manager (something like 7-zip or rar) to extract the contents into a folder you'll be running MMV.

#### 2. Using git CLI

Install git  Windows the installer from [git downloads page](https://git-scm.com/downloads)

Open a shell on desired dir to clone the repo (GIT bash shell on Windows)

`git clone https://github.com/Tremeschin/modular-music-visualizer`

<hr>

### If running with Anaconda

Open the Anaconda shell from start menu, then we'll create an conda environment and activate it:

- `conda create --name mmv python=3.8`

- `conda activate mmv`

Now with basic CLI navigation commands, change to the directory you extracted or downloaded MMV, if it's on your Downloads folder, when executing the anaconda shell you should be at `C:\\users\your_user` so run:

- `cd .\Downloads\modular-music-visualizer-master\mmv`

Or just take the path on Windows Explorer and do:

- `cd "C:\\path\to\mmv\with\ugly\back\slashes"`

<hr>

### If running with vanilla Python

Open a shell on the downloaded and extracted folder

On Windows you can right click an empty spot on the Windows File Manager app while holding the shift key for a option to "Open PowerShell" here to appear.

Change the working directory of the shell to the folder `ROOT/mmv_skia` (or just execute the previous step on that folder which contains the file `example_basic.py`)

This step is not required but good to do so, create an virtual environment (venv) and activate it:

- `python.exe -m venv mmv-venv`

- `.\venv-path\Scripts\activate.bat`

<hr>

**Chose:**

#### 1. Vanilla Python: automatic installation and running

When you run `python .\example_basic.py --auto-deps` it should take care of downloading and installing Python dependencies as well as FFmpeg by downloading from https://www.gyan.dev/ffmpeg/builds/ and extracting to a temp folder, moving the binary to the right place.

If you're on anaconda, perhaps running with `--user` as so: `python .\example_basic.py --auto-deps --user` should fix permission errors.

If this process doesn't work (dead links for example), report any issue you had. You can also continue reading this for manual instructions.

<hr>

#### 2. Vanilla Python: manual FFmpeg and Python deps installation

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary named `ffmpeg.exe` must be on the directory `ROOT/mmv_skia/mmv/externals/ffmpeg.exe`.

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

Run MMV with `python .\example_basic.py`

<hr>
<p align="center">
  <i>Either by following path 1 or 2 you should have your final default video on the `renders` folder after running `example_basic.py` script.</i>
</p>
<hr>

## Editing configs

Pass flag `mode=music` or `mode=piano` for a quick swap between the two: `python example_basic.py --auto-deps mode=[music,piano]`.

The flag `--auto-deps` is not required after the first successful run. For macOS the `--user` flag is also not needed, but run it together with `--auto-deps` whenever you'll use that.

Everything I considered useful for the end user is under `example_basic.py` controlled by upper case vars such as `INPUT_AUDIO`, `MODE`, `OUTPUT_VIDEO`, etc.

Change those or keep reading the file for extra configurations.

If you're going to venture out on creating your own MMV scripts or hacking the code, making new presets, I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfalls.

Though you probably should be fine by just creating a copy of the example scripting I provide on the repo and reading through my comments and seeing the Python code working, it's pretty straightforward the top most abstracted methods as I tried to simplify the syntax and naming functions with a more _"concrete"_ meaning. 

At one point I'll have a proper wiki on every argument we can send to MMV objects.

<hr>