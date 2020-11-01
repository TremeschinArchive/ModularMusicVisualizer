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

![Demo image of MMV](repo/music-2.jpg)

This screenshot is from a track of mine I released using MMV!!

_The DAW is Ardour 6.0_

[Link on YouTube](https://www.youtube.com/watch?v=KRI9cKPsK1Q) (Music Bars)

<hr>

![Demo image of MMV Piano Roll](repo/piano-roll-3.jpg)

[Link on YouTube](https://youtu.be/CoFoRsoerjk) (Piano Roll)

This screenshot is the piano tutorial of the previous music track!

<hr>

# Idea

I am a Free and Open Source music producer hobbyist that also happens to be a code hobbyist and at some point it's inevitable I'd be releasing my tracks to the internet and create some project to make the world a better place.

The problem is, I don't want to release a video of the track on a platform with a static image or just recording the screen nor pay for some software to generate an "music visualization" for me without much control of it.

So I searched up for a free (as in freedom and price) tool that does exactly that, they do exist but aren't as good as they could be, most of the time a bit basic..

Then I just got into this opportunity on making a suckless (as in quality not minimalism I see you lol) music visualization tool with the programming languages and tools I love and care.

I also gently ask you to read about the [Free Software Definition / Philosophy](https://www.gnu.org/philosophy/free-sw.html) and join us!! :)

<hr>

# Table of contents

   * [Community, Support, Help](#community-support-help)
   * [Hacking the Code](#hacking-the-code)
   * [Running](#running)
      * [Linux](#linux)
      * [Windows](#windows)
   * [Goals, what is being developed](#goals-what-is-being-developed)
   * [Contributing](#contributing)
   * [User Generated Content, legal](#user-generated-content-copyrighted-material-legal)

<hr>

# Community, Support, Help

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer, I think it'll be the healthiest one for this project.

Expect MMV to be forever Free (price and freedom).

In the future I'll write my thoughts on my blog (you can find the link on my profile for the main website) about these topics: licensing, money, developers, freedom, etc.

<hr>

# Wiki is TODO

Lot's of stuff are moving on the code and being rewritten, when things are more stable I'll write a proper guide.

The `example_basic.py` script covers most of MMV's "balanced" functionality, 

## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

<hr>

# Running

This project wasn't extensively tested on Windows, feedback appreciated.

Instructions I refer to the Linux os should be the same under MacOS as both comes from a common ancestor (UNIX) and utilizes the `bash` shell.

MacOS users might use `homebrew` for installing stuff such as Python and FFmpeg, help and feedback required for steps and if it even works there.

## IMPORTANT!!

### YOU MUST USE A 64 BIT PYTHON INSTALLATION

`skia-python` package only includes 64 bit wheels on PyPI as Skia 32 bits is not available for the public.

### General recomendations

If you're going to venture out on creating your own MMV scripts or hacking the code, making new presets, I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfals.

Though you probably should be fine by just creating a copy of the example scripting I provide on the repo and reading through my comments and seeing the Python code working, it's pretty straightforward the top most abstracted methods as I tried to simplify the syntax and naming functions with a more _"concrete"_ meaning. 

<hr>

## Linux / Windows

I will be referring to where the source code folder of MMV is located at using the keyord `ROOT`, like the `LICENSE.md` file under `ROOT/LICENSE.md`.

Note: on Windows you might need to replace `python` with `python.exe` if using PowerShell (recommended) or CMD (I'm not completely sure btw) 

Another point is that directories on Windows uses `\` instead of (what everything else uses) `/`, Python should convert those automatically but maybe not within the shell, like: `.\path\to\executable.exe` instead of `./path/to/executable.exe`, the second one might not run. This does not apply on the Python scripts as it'll auto convert `/` to `\\`.

### Install Python 64 bits (REQUIRED) and FFmpeg

<hr>

#### Linux:

- Arch Linux / pacman based (Manjaro): `sudo pacman -Syu python python-setuptools ffmpeg`

- Ubuntu / apt based: `sudo apt update && sudo apt install python3 python3-venv python3-dev python3-setuptools ffmpeg`

<hr>

#### Windows:

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer)

##### Now we'll need FFmpeg

When you run `example_basic.py`, it should take care of FFmpeg by downloading from https://www.gyan.dev/ffmpeg/builds/ and extracting, adding to the environmental PATH. If it doesn't work, report any issue, you can also continue reading this for manual instructions.

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary must be available within PATH environment for `ffmpeg-python` package to use.

Either add to PATH environment var a folder with `ffmpeg.exe` binary if you know or drop FFmpeg's binary into the same directory as the `example_*.py`.

<hr>

### Installing Pillow-SIMD for faster performance

While this package is not required and you can keep the default Pillow package, using [pillow-simd](https://github.com/uploadcare/pillow-simd) instead of the vanilla package, as you can see [here](https://python-pillow.org/pillow-perf/), is indeed faster, however Pillow isn't the biggest bottleneck in the code, so you'd get performances (guessing) at most 10% faster.

Currently only rotating the images uses the PIL project.

Install the listed [prerequisites](https://pillow.readthedocs.io/en/stable/installation.html#building-from-source) according to your platform on their documentation, and as mentioned on the main repo README, install `pillow-simd` with:

```bash
$ pip uninstall pillow
$ pip install pillow-simd
```

If you want you can use AVX2 enabled build installation with:

```bash
$ pip uninstall pillow
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```

You can safely skip this section and use regular Pillow, but with longer render times this few performance gains can stack a lot.

<hr>

### Getting the source code

#### Using git CLI

Install git from your Linux distro or for Windows the installer from [git downloads page](https://git-scm.com/downloads)

Open a shell on desired dir to clone the repo (GIT shell on Windows)

`git clone https://github.com/Tremeschin/modular-music-visualizer`

#### GitHub / GitLab repository main page

You might be already here, head to the top page and there is a (green for GitHub, blue for GitLab) button _"⬇️ Code"_ and download as a ZIP.

Use a archive manager (something like 7-zip or rar) to extract the contents into a folder you'll be running MMV.

<hr>

## Open a shell on MMV source code folder

Change your directory to the `mmv` folder, both Linux and Windows should be `cd mmv`, or just open the terminal there at first place.

You also can use the command `ls` (Original one on Windows is `dir`) on both OSs to list the files on the current directory and type `pwd` to "Print Working Directory" (Windows should be `echo %cd%` or PowerShell auto converts it?)

I recommend PowerShell on Windows or your preferred terminal emulator on Linux using bash for this

On Windows you can right click an empty spot on the Windows File Manager app while holding the right mouse button for a option to "Open PowerShell" here to appear.

<hr>

## Installing Python dependencies

It is not a bad idea to install MMV dependencies on a separate virtual environment of Python packages to keep things isolated.

[Quick guide on using / creating Python venvs](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs):

If you're not sure what you're doing here, while you can skip this section I'd recommend not to.

- `python -m venv mmv-venv`

- Linux: `source ./mmv-venv/bin/activate`

- Windows (not sure): `.\venv-path\Scripts\activate.bat`

After that you can point Python's package installer (pip) the file located at `ROOT/mmv/mmv/requirements.txt`

`pip install -r ./mmv/mmv/requirements.txt`, assuming your shell is under `ROOT` directory.

You can run a example file under `ROOT/mmv/example*.py` with `python ROOT/mmv/example*.py` where `*` is the substring on the file.

Currently most of MMV functionality is exposed under the `example_basic.py` file, definitely read the whole file for a usage guide, there's a lot of variables right at the top for quick changing stuff, modes (Piano Roll, Music), enabling and disabling effects, etc.

I include a few free assets under the `mmv/assets/free_assets` folder, you can use them at your disposal, others are generated on the go, see running script of MMV for more details.

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
