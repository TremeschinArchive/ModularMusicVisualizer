<p align="center">
    <img src="repo/mmv-project-logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  An attempt to make a free (as in freedom) and open source music visualization (After Effects and Synthesia)-like tool for the music production community.
  <br><hr>
  <i>Support for Music Bars mode, Piano Roll tutorials, Video as background, enable / disable whatever you want. Hack the code at your will.</i>
</p>
<hr>

- **No watermark, pay walls or any crap.**

<p>

- **Simply a full featured music visualization software**

<p>

- **Everything available at no cost.**

<p>

- **Everything configurable.**

<hr>
Officially works on Linux and Windows, high chance of working on macOS and BSD (more info below)
<hr>

## Showcase

![Demo image of MMV](repo/music-mode.jpg)

This screenshot is from a track of mine I released using MMV!!

_The DAW is Ardour 6.0_

[Link on YouTube](https://www.youtube.com/watch?v=KRI9cKPsK1Q) (Music Bars)

<hr>

![Demo image of MMV Piano Roll](repo/piano-roll.jpg)

[Link on YouTube](https://youtu.be/CoFoRsoerjk) (Piano Roll)

This screenshot is the piano tutorial of the previous music track!

<hr>

# Idea

I am a Free and Open Source music producer and code hobbyist and at some point it's inevitable I'd be releasing my tracks to the internet and create some project to make the music industry less harsh and more accessible.

The problem is, I don't want to release a music video on a platform with a static image or just recording the screen, nor pay for *some software* to generate an "music visualization" for me without much control of it, taking out all the fun on hacking the non open source code.

So I searched up for a free **(as in freedom and price)** tool that does exactly that, they do exist but aren't as good as they could be, most of the time a bit basic.

I embraced this opportunity on making a suckless music visualization tool (a more traditional approach than 3D random nonsense) with the programming languages and tools I love and care.

I also invite you to read about the [Free Software Definition / Philosophy](https://www.gnu.org/philosophy/free-sw.html) and join us on this amazing community!! :)

*Let's make music more accessible for small producers and keep it affordable for such tallented people, I'm doing my part, are you doing yours?*

<hr>

# Table of contents

   * [Community, Support, Help](#community-support-help)
   * [Hacking the Code](#hacking-the-code)
   * [Running](#running)
      * [Linux](#linux)
      * [Windows](#windows)
   * [Editing configs](#editing-configs)
   * [Goals, what is being developed](#goals-what-is-being-developed)
   * [Contributing](#contributing)
   * [User Generated Content, legal](#user-generated-content-copyrighted-material-legal)

<hr>

# Community, Support, Help, Donations

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer working "full time" or "serious" on a project, I think it'll be the healthiest one for this project.

**Expect MMV to be forever Free (price and freedom).**

<hr>

## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

Feel free DM me, I'd be happy to explain how MMV works.

<hr>

# Running

I'll be referring to where the source code folder of MMV is located at using the keyword `ROOT`, like the `LICENSE` file under `ROOT/LICENSE`.

You'll mainly need to use basic command line interface and navigation such as `cd` (change directory), `mkdir` (make directory), `pwd` (print working directory). Don't be afraid of searching how those work on Windows because I am very rusty on its CLI. On the other OSs, most should be POSIX compliant and literally use the same command.

Linux users can now skip to the next section.

**Note**: on **Windows** you might need to replace `python` with `python.exe` if using PowerShell (recommended) or CMD (I'm not completely sure btw).

Another point is that directories on Windows uses `\` instead of (what everything else uses) `/`, Python should convert those automatically, however the shell (where you call commands) might not convert those like `.\path\to\executable.exe` instead of `./path/to/executable.exe`, the second one might not run on Windows. This does not apply on the Python scripts as it'll auto convert `/` to `\\`.

This project isn't extensively tested on Windows, feedback appreciated.

## IMPORTANT!!

<hr>

### YOU MUST USE A 64 BIT PYTHON INSTALLATION

`skia-python` package only includes 64 bit wheels on PyPI as Skia 32 bits is not available for the public.

The code will check itself for a 64 bit installation and quit if not.

<hr>

### YOU MUST USE A PYTHON < 3.9

`skia-python` package only includes its package wheels (installation files) up until Python 3.8, also most Linux distros and even Homebrew on macOS don't come with Python 3.9 by default yet, so 3.8 is the "latest working and version norm".

<hr>

# Installing Python, FFmpeg and dependencies

Also see [EXTRAS.md](docs/EXTRAS.md) file for squeezing some extra performance.

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

  - `sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev` 

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

I did get a few OpenGL errors when doing this as I was using a mac VM with the scripts of this repo: https://github.com/foxlet/macOS-Simple-KVM

**Disclaimer:** I just installed the system for testing my code, I won't use any products I don't own there, I just want to support many platforms but I both don't have and don't know someone that owns a proper macbook. This was the cheap and dirty sollution of it I was sure I'd get a few errors there, but most stuff went fine.

Feedback wanted on native macOS, this is as far as I can help you for now.

See after Windows section for info on configuring your own stuff or click [HERE](#editing-configs)

## Windows:

<p align="center">
  <i>Prepare your disks and patience!!</i>
</p>

Any easier steps for Windows are welcome specially for external installs other than Python that are needed.

**Chose:**

##### 1. With Anaconda (less trouble)

Download and install `Anaconda` (not `miniconda`), make it your default Python optimally on the installer.

##### 2. With vanilla Python (discouraged somehow)

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer).

You'll also need to download `Build Tools for Visual Studio` which got merged into Visual Studio Community Edition, so search that (Build Tools for VS) and download the installer of the VS Community.

You'll need to install the whole C++ development package group so Python can use a compiler and the Windows SDK for building dependencies such as numpy. This will use quite a bit of disk space and definitely will take a while to complete. After that you can proceed to the next steps.

Search for `scipy` Python wheels and install the version listed on `requirements.txt`.

For this last step you can also manage to install lapack or blas / openblas on your system. I could not. This is finicky and I offer no official support for this.

### Important: extra step for an automatic installation of dependencies

Go to [7-zip downloads](https://www.7-zip.org/download.html) website, download the `7-Zip for 64-bit Windows x64 (Intel 64 or AMD64)` executable if you don't have it already installed, run it and extract the files on the default path.


This step is required to extract the video encoder (FFmpeg) compressed files if you don't want to do this by hand.

<hr>

### Getting the source code

#### GitHub / GitLab repository main page

You might be already here, head to the top page and there is a (green for GitHub, blue for GitLab) button _"⬇️ Code"_ and download as a ZIP.

Use a archive manager (something like 7-zip or rar) to extract the contents into a folder you'll be running MMV.

#### Using git CLI

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

### If running with vanilla Python

Open a shell on the downloaded and extracted folder

On Windows you can right click an empty spot on the Windows File Manager app while holding the shift key for a option to "Open PowerShell" here to appear.

Change the working directory of the shell to the folder `ROOT/mmv` (or just execute the previous step on that folder which contains the file `example_basic.py`)

This step is not required but good to do so, create an virtual environment (venv) and activate it:

- `python.exe -m venv mmv-venv`

- `.\venv-path\Scripts\activate.bat`

**Chose:**

#### 1. Vanilla Python: automatic installation and running

When you run `python .\example_basic.py --auto-deps` it should take care of downloading and installing Python dependencies as well as FFmpeg by downloading from https://www.gyan.dev/ffmpeg/builds/ and extracting to a temp folder, moving the binary to the right place.

If you're on anaconda, perhaps running with `--user` as so: `python .\example_basic.py --auto-deps --user` should fix permission errors.

If this process doesn't work (dead links for example), report any issue you had. You can also continue reading this for manual instructions.

#### 2. Vanilla Python: manual FFmpeg and Python deps installation

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary named `ffmpeg.exe` must be on the directory `ROOT/mmv/mmv/externals/ffmpeg.exe`.

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

Run MMV with `python .\example_basic.py`

<hr>

Either path 1 or 2 you should have your final default video on the `renders` folder after running `example_basic.py` script.

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

# Goals, what is being developed

Also see [CHANGELOG.md](CHANGELOG.md) file :)

I have also some experiments on `mmv/experiments` folder, some not totally related to MMV and might become a separate project but they are here because I'm reusing some functionality of MMV and might also merge them in the future.

#### Next stuff

- [ ] *CAN BE EXPANDED* (30%) Progression bar (square, circle, pie graph?)

- [ ] Implement text support (lyrics.. ?)

- [ ] Load and configure MMV based on a YAML file, so distributing binaries will be theoretically possible

- [ ] Rain images on pygradienter and rain particle generator?

#### Ideas for the future or waiting to be executed

- [ ] Rectangle bars visualizer (only circle + linear or symmetric currently)

#### Impossible / hard / dream

- [ ] Make MMV Piano Roll interactive for learning, writing midi files?

- [ ] (Help needed) Fully functional and configurable GUI (trying PySimpleGui, DearPyGui didn't really fit)

# Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) file :)

This repository on GitHub is a mirror from the main development repository under [GitLab](https://gitlab.com/Tremeschin/modular-music-visualizer), I'm mostly experimenting with the other service and balancing out as my other project [Dandere2x Tremx](https://github.com/Tremeschin/dandere2x-tremx) is -hub only.

I didn't set up bidirectional mirroring as that can cause troubles, GitLab automatically pushed every change I make to GitHub.

Feel free to create issues on any of both platforms, PRs / Merge Requests I ask you to do under GitLab (as I'm not sure what would happen if I accept something here? perhaps some protected branches shenanigans to solve this?).

# User Generated Content, copyrighted material, legal

Any information, images, file names you configure manually is considered (by me) user generated content (UGC) and I take no responsibility for any violations you make on copyrighted images, musics or logos.

I give you a few "free assets" files, those, apart from the MMV logo I created myself on Inkscape, were generated with Python with some old code written by me, you can use them freely. Some are generated on the go if configured (they are on by default) on the running script of MMV.


# Honest word

Don't abuse from your freedom the power to ascend with this software with much hard work put on it.

Pay back your fees with a simple **"Thank you"** at least.

It doesn't seem much but pursuing something others also keep an expectancy or genuinely changed their lifes for good is a hell of a great motivation: **being awknowledged not for feeling superior or meaningless better, but for being helpful, making a diference, gratitude.**

*Don't take this as an obligation, you're free, this software is free.*

The Modular Music Visualizer project definitely changed my life, I grew up so much as a programmer, my problem solving skills accuracy and speed improved a lot, not to mention general organization of stuff.. I'm already victorious on the existence and execution of such code.

Can't forget to **thank a lot all the people behind all the dependencies I used in this project**. We don't need to come up with pythagoras theorem from scratch anymore as someone did that for us in the past. Just like I don't need to make an complex video encoder, there's the FFmpeg team already. Old generations making a better world and time for future ones.

# Thank You

My sincere Thank You if you read the README all the way until here, hopefully you learned something new.


