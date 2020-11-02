<p align="center">
    <img src="repo/mmv-project-logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  An attempt to make a free (as in freedom) and open source music visualization (After Effects and Synthesia)-like tool for the music production community.
  <br><hr>
  <i>Support for Music Bars mode, Piano Roll tutorials, Video as background, enable / disable whatever you want.</i>
</p>
<hr>


## Small showcase

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

The problem is, I don't want to release a music video on a platform with a static image or just recording the screen, nor pay for some software to generate an "music visualization" for me without much control of it.

So I searched up for a free (as in freedom and price) tool that does exactly that, they do exist but aren't as good as they could be, most of the time a bit basic.

Then I just got into this opportunity on making a suckless (not suckless.org lol) music visualization tool with the programming languages and tools I love and care.

I also invite you to read about the [Free Software Definition / Philosophy](https://www.gnu.org/philosophy/free-sw.html) and join us on this amazing community!! :)

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

# Community, Support, Help

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer working "full time" or "serious" on a project, I think it'll be the healthiest one for this project.

Expect MMV to be forever Free (price and freedom).

<hr>

## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

<hr>

# Running

This project isn't extensively tested on Windows, feedback appreciated. MacOS instructions should be similar or equal to Linux ones, though feedback required for steps and if it even works there.

I'll also be referring to where the source code folder of MMV is located at using the keyword `ROOT`, like the `LICENSE` file under `ROOT/LICENSE`.

**Note**: on **Windows** you might need to replace `python` with `python.exe` if using PowerShell (recommended) or CMD (I'm not completely sure btw).

Another point is that directories on Windows uses `\` instead of (what everything else uses) `/`, Python should convert those automatically, however the shell (where you call commands) might not convert those like `.\path\to\executable.exe` instead of `./path/to/executable.exe`, the second one might not run on Windows. This does not apply on the Python scripts as it'll auto convert `/` to `\\`.

You'll mainly need to use basic command line interface and navigation such as `cd` (change directory), `mkdir` (make directory), `pwd` (print working directory). Don't be afraid of searching how those work on Windows because I am very rusty on its CLI.

Also see [EXTRAS.md](docs/EXTRAS.md) file for squeezing some extra performance.

## IMPORTANT!!

### YOU MUST USE A 64 BIT PYTHON INSTALLATION

`skia-python` package only includes 64 bit wheels on PyPI as Skia 32 bits is not available for the public.

The code will check itself for a 64 bit installation and quit if not.

<hr>

### Installing Python, FFmpeg, dependencies

## Linux:

- Arch Linux / pacman based (Manjaro): `sudo pacman -Syu python python-setuptools ffmpeg git`

- Ubuntu / apt based: `sudo apt update && sudo apt upgrade && sudo apt install python3 python3-venv python3-dev python3-setuptools ffmpeg git`

Open a shell on a directory and clone the repo:

- `mkdir ~/mmv && cd ~/mmv` (creates `mmv` folder on your home dir)

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/mmv`

Preferably use a virtual environment:

- `python -m venv mmv-venv`

- `source ./mmv-venv/bin/activate`

Then run `python example_basic.py`

It should install Python dependencies automatically, if not run `pip install ./mmv/requirements.txt`

MMV should then run and generate the default video with default preset under the `renders` directory.

<hr>

## Windows:

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer).

##### Extra step for an automatic installation of dependencies

Go to [7-zip downloads](https://www.7-zip.org/download.html) website, download the `7-Zip for 64-bit Windows x64 (Intel 64 or AMD64)` executable if you don't have it already, run it and extract the files on the default path. This step is required to extract the video encoder (FFmpeg) compressed files if you don't want to do this by hand.

<hr>

### Getting the source code

#### GitHub / GitLab repository main page

You might be already here, head to the top page and there is a (green for GitHub, blue for GitLab) button _"⬇️ Code"_ and download as a ZIP.

Use a archive manager (something like 7-zip or rar) to extract the contents into a folder you'll be running MMV.

#### Using git CLI

Install git  Windows the installer from [git downloads page](https://git-scm.com/downloads)

Open a shell on desired dir to clone the repo (GIT shell on Windows)

`git clone https://github.com/Tremeschin/modular-music-visualizer`

<hr>

Open a shell on the downloaded and extracted folder

On Windows you can right click an empty spot on the Windows File Manager app while holding the shift key for a option to "Open PowerShell" here to appear.

Change the working directory of the shell to the folder `ROOT/mmv` (or just execute the previous step on that folder which contains the file `example_basic.py`)

#### Automatic installation and running

When you run `python.exe .\example_basic.py` it should take care of downloading and installing Python dependencies as well as FFmpeg by downloading from https://www.gyan.dev/ffmpeg/builds/ and extracting to a temp folder, moving the binary to the right place.
 
If this process doesn't work (dead links for example), report any issue you had. You can also continue reading this for manual instructions.

#### Manual installation

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary named `ffmpeg.exe` must be on the directory `ROOT/mmv/mmv/externals/ffmpeg.exe`.

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

Run MMV with `python .\example_basic.py`

<hr>

Automatic or manual installation you'll have your final default video on the `renders` folder after running `example_basic.py` script.

<hr>

### Editing configs

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
