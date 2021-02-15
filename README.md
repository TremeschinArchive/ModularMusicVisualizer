<p align="center">
    <img src="repo/mmv_logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  High quality video music visualization tool for the music production community.
  <br><hr>
  <i>Support for Music Bars and Piano Roll mode, Video as background, enable / disable whatever you want. Hack the code at your will. Real Time mode for live DJing</i>
</p>
<hr>

- **Simply a full featured music visualization software.**

<p>

- **No watermark, pay walls or any crap.**

<p>

- **Everything available at no cost.**

<p>

- **Everything configurable.**

<hr>
Officially works on Linux with all features, most work on macOS and Windows
<hr>

## Showcase

![Demo image of MMV](repo/mmv-shader-1.png)
_^ This runs real time 60 fps+ depending on your GPU and CPU using GLSL shaders_

More on performance later

<hr>

![Demo image of MMV Piano Roll](repo/piano-roll-4.jpg)
_^ "Old code" which is currently used to draw the piano roll_

[Link on YouTube](https://www.youtube.com/watch?v=NwP5LESrceY) (Piano Roll Mode)

<hr>

![Demo image of MMV](repo/music-mode-2.jpg)
_^ Also "old code" with previous visuals before Shaders_

[Link on YouTube](https://www.youtube.com/watch?v=5cUhRTab4Ks) (Music Bars Mode)



<hr>

# Idea

I am a Free and Open Source music producer and code hobbyist, at some point I'd be releasing my tracks to the internet and create some project to make the music industry less harsh and more accessible, that was once my thought.

The problem is, I don't want to release a music video on a platform with a static image or just recording the screen, nor pay for some software to generate an "music visualization" for me without "much control" of it, taking out all the fun on hacking the non open source code.

So I searched up for a free **(as in freedom and price)** tool that does exactly that, they do exist but aren't as good as they could be, most of the time a bit basic or random looking.

I embraced this opportunity on making a suckless music visualization tool with the programming languages and tools I love and care.

I cannot deny I took some heavy inspiration on 3blue1brown's [Manim](https://github.com/3b1b/manim) project, specifically the way we configure the MObjects there and simply add attributes, ask them to be drawn. While both are very different projects their usability are somewhat similar in a core level of how to operate.

I also invite you to read about the [Free Software Definition / Philosophy](https://www.gnu.org/philosophy/free-sw.html) and join us on this amazing community!! :)

*Let's make music more accessible for small producers and keep it affordable for such talented people, are you doing your part?*

<hr>

# Table of contents

   * [Community, Support, Help](#community-support-help)
   * [Running](#running)
   * [Common problems, FAQ, tips](#common-problems-faq-tips)
   * [Hacking the Code](#hacking-the-code)
   * [Performance](#performance)
   * [Goals, what is being developed](#goals-what-is-being-developed)
   * [Contributing](#contributing)
   * [User Generated Content, legal](#user-generated-content-copyrighted-material-legal)
   * [License](#license)
   * [Acknowledgements | Thanks to](#acknowledgements-thanks-to)

<hr>

# Community, Support, Help, Donations

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer working "full time" or "serious" on a project, I think it'll be the healthiest one for this project.

**Expect MMV to be forever Free (price and freedom).**

<hr>

# Running

**Important: The project is under some heavy rewiring and R&D, have yet to normalize instructions and documentation, I can't test everything after every commit so expect minor bugs.** Also there is technically two projects in the same repository ("old" MMVSkia and new MMVShader) sharing some common files, keeping compatibility while rewriting stuff is a bit tricky and is the main source of current problems.

## Python

Please install Python 3.8 (hard requirements are _V >= 3.7_ potentailly), Python 3.9 should work™ but _can_ act weird. Give 3.9 a shot otherwise downgrade to 3.8 if you get weird dependency related stuff.

**Only a 64 bits OS will work**, most of you should have it.

The easiest way to run MMV is by using an alternative community Python "package manager" called [Poetry](https://github.com/python-poetry/poetry), it automatically will create environments (containers) for MMV's dependencies and install it for you.

Alternatively you can chose not to use poetry but the regular `requirements.txt` of Python.

First you have to install Python:

<hr>

### Installing Python

_Linux and macOS have optional dependency `musescore` to convert midi files to audio when using Skia + Piano Roll mode_

**Note**: On Windows use `python.exe`, `python3.exe` or `python3.8.exe` (the one you have) on Python commands, Linux and macOS will use either `python38`, `python3.8` or simply `python`. I'd say with with only `python` on L/M and `python.exe` on Windows if you have only one version of Python installed.

**Windows Note:** Windows uses ugly backslashes `\` rather than forward slashes `/` when referring to files and directories. Replace those to yours equivalent OS separator.

<hr>

- **Windows:** Head over to [Python dot org](https://www.python.org/downloads/windows/), download **Python 3.8.3 Windows x86-64 executable installer**, install it and make sure to **check the box "Add Python 3.8.6 to PATH"**

<hr>

- **Linux:** Install Python and other deps from your package manager, for example:
  - *Arch Linux, Manjaro, pacman-based:* `sudo pacman -Syu base-devel git ffmpeg python38 musescore python-poetry`
  - *Ubuntu:* `sudo apt update && sudo apt upgrade && sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev build-essential`
  - *Fedora:* `sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm && sudo dnf upgrade && sudo dnf install python-devel ffmpeg git blas openblas lapack atlas libgfortran atlas-devel gcc-c++ gcc-gfortran subversion redhat-rpm-config python38 musescore`
  - *OpenSUSE:* `sudo zypper install git ffmpeg musescore`

Outside Python the other required dependency for rendering to video files on either part of MMV project is [FFmpeg](http://ffmpeg.org/).

<hr>

- **macOS:** I don't have the hardware to test nor proper knowledge but should be something like:
  - Install [Homebrew](https://brew.sh/)
  - `brew install python@3.8 ffmpeg musescore git`

<hr>

_Note for Linux:_ Pacman based distros have `python-poetry`, I am unsure about the other ones but you can skip this next step of getting Poetry since you should have it.

<hr>

### (Poetry way) Installing Poetry

Follow instructions on [Poetry's README](https://github.com/python-poetry/poetry#installation) or install from your package manager.

On **Windows** I think it's easier to run `python.exe -m pip install poetry --user` on PowerShell or Command Prompt rather than their curl script or cloning the repo, I had no issues running MMV there with this.

### Getting the Source Code of MMV

Either go to the main repository page at [GitHub](https://github.com/Tremeschin/modular-music-visualizer), click the green down arrow saying "Code", extract to somewhere

Or just `git clone https://github.com/Tremeschin/modular-music-visualizer` if you have GIT CLI

### Installing Dependencies

Open a shell on the folder where you extracted MMV (shift + right click empty space on Windows, _"Open PowerShell here"_), Linux and macOS users should be able to change the working directory into the folder (basic shell navigation) or by right clicking your file manager (at least Nautilus, Dolphin with extension)

#### Poetry

Run:

- `poetry install`

_(Binary is `poetry.exe` on Windows if you're on PowerShell or just `poetry` if on old Command Prompt)_

#### Vanilla way (requirements.txt)

Run:

- `python -m venv mmv_env`
  - Linux: `source ./mmv_env/bin/activate`
  - Windows: `source .\mmv_env\bin\activate.bat`

- `python -m ensurepip`
- `python -m pip install wheel`
- `python -m pip install -r ./requirements.txt`

You'll need to activate the virtualenv (sourcing it) every time you run MMV.

## Actually Running

Configure the files `/src/run_shaders.py` or `/src/run_skia.py` to your needs (images, audios) _[though there is a default configuration, if you want fast results skip this]_

I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfalls.

### Poetry:

- `poetry run shaders`: View realtime
- `poetry run shaders render`: Render target audio file to video
- `poetry run skia` [same as] `poetry run skia mode=music`: Render target audio file to video
- `poetry run skia mode=piano`: Render target audio file + midi to video

These will only work if your shell working directory is on the root of the source code, alternatively run:

- `poetry run python ./src/run_shaders.py`: View realtime
- `poetry run python ./run_shaders.py`: View realtime
- `poetry run python ./run_shaders.py render`: Render target audio file to video
- ... depending where your working directory is

### Vanilla Python:

Good to change the directory to the `src` dir: `cd ./src`

- `python run_shaders.py`: View realtime
- `python run_shaders.py render`: Render target audio file to video
- `python run_skia.py` [same as] `python run_skia.py mode=music`: Render target audio file to video
- `python run_skia.py mode=music`: Render target audio + midi file to video
  
<hr>

# Common problems, FAQ, tips

## (Shaders) No audio responsiveness, wrong recording device

By default MMV takes the first loopback device it finds, mostly in alphabetical order so if you have a VR headset plugged on, some weird audio setup with multiple audio interfaces it might get the wrong one.

Fixing this is simple, run `poetry run shaders list` or `python run_shaders.py list`, it'll list the devices in your computer like:

```log
$ poetry run shaders list
[run_shaders.py] Available devices to record audio:
[run_shaders.py] > (0) [Jack source (PulseAudio JACK Source)]
[run_shaders.py] > (1) [Monitor of Jack sink (PulseAudio JACK Sink)]
```

Then you just run it with the `capture flag`:

- `poetry run shaders capture=1` or `python run_shaders.py capture=1`

In my case, `capture=1` is the audio from the computer and `capture=0` is my microphone itself, so we can also have a IRL interactive mode of some sort.

## (RT Shaders) Want more aggressiveness

Pass argument `multiplier=N` to `poetry run shaders multiplier=160` or some other number to increase how harsh MMV will react to audio amplitudes and frequencies. 

Of course you can just bump the volume up but it's no good because it hurts your hearing, if you want more emotion at a lower volume.

Also works for rendering mode.

TODO: configure this on the real time window itself.


## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

Feel free DM me, I'd be happy to explain how MMV works.

# Performance

I was able to sustain even 144 fps on my mid level hardware of 2019, running Jack Audio on Linux with 128, 256, 512 samples of audio buffer, though I'd recommend 256 or 512 just in case we miss some data.

It highly depends on the settings you use like resolution, target fps and the audio processing's batch size, but it was more than enough for live DJing while having a full DAW playing audio in the background.

I'm quite new to GLSL programming and my shaders can definitely be improved at least 4x more speeds and efficiency, but oh well GPUs are damm fast.

Also my audio processing processes stuff with `BATCH_SIZE = 2048 * 4` at about 230 FPS on my CPU, so we're technically limited by this when rendering plus your GPUs raw compute power, memory bus transfer speeds.

It definitely saturates my CPU with the video encoder, 100% constant usage.

# Goals, next idea

Also see [CHANGELOG.md](CHANGELOG.md) file :)

**Configuring the MMVShader is currently not possible, writing some MMVShaderMaker will take a while. Be patient. This is sorta main priority**

- [ ] Progression bar (square, circle, pie graph?)

- [ ] Implement text support (lyrics.. ?)

- [ ] Load and configure MMV based on a YAML file, so distributing binaries will be theoretically possible

- [ ] Generate rain droplets using shaders

- [ ] Make MMV Piano Roll interactive for learning, writing midi files?

- [ ] (Help needed) Fully functional and configurable GUI

<hr>

# Contributing

This repository on GitHub is a mirror from the main development repository under [GitLab](https://gitlab.com/Tremeschin/modular-music-visualizer), I'm mostly experimenting with the other service.

I didn't set up bidirectional mirroring as that can cause troubles, GitLab automatically pushed every change I make to GitHub.

Feel free to create issues on any of both platforms, PRs / Merge Requests I ask you to do under GitLab (as I'm not sure what would happen if I accept something here? perhaps some protected branches shenanigans to solve this?).

<hr>

# User Generated Content, copyrighted material, legal

Any information, images, file names you configure manually is considered (by me) user generated content (UGC) and I take no responsibility for any violations you make on copyrighted images, musics or logos.

I give you a few "free assets" files, those, apart from the MMV logo I created myself on Inkscape, were generated with Python with some old code written by me, you can use them freely. Some are generated on the go if configured (they are on by default) on the running script of MMV.

# License

Currently all the files of this repository are licensed under the GPLv3 license, some functions are CC and I kept those attributed with the original creator, so check every file beforehand.

I might MIT the GLSL shaders files in the future, depends on my will (I'm currently 35% favorable of this idea).

# Acknowledgements, Thanks to

I want to show my gratitude to these projects, no joke, MMV wouldn't be possible if these projects didn't exist.

Those are not in order of importance at all, they are always used together.

I'll mainly list the main name and where to find more info, it's just impossible to list every contributor and person that took place into those.

### Main ones

- Python language (https://www.python.org), where development speed is also a feature.

- [Skia-Python wrapper](https://github.com/kyamagu/skia-python), for a stable Python interface with the [Skia Graphics Library](https://skia.org).
  
  - Generates the base videos and piano roll mode graphics.

- [ModernGL Python package](https://github.com/moderngl/moderngl) for making it simple to render fragment shaders at insane speeds under Python.
  
  - Also the ModernGL (current?) main developer [einarf](https://github.com/einarf) for helping me an substantial amount with some good practices and how to do's
  
- [FFmpeg, FFplay](https://ffmpeg.org), _"A complete, cross-platform solution to record, convert and stream audio and video."_ - and they are not lying!!

  - "The Only One". Transforms images into videos, adds sound, filters.

- The [GLSL](https://en.wikipedia.org/wiki/OpenGL_Shading_Language) language, OpenGL, Vulkan (on mpv flag), the [Khronos group](https://www.khronos.org) on its entirety, seriously, you guys are awesome!!

  - Also the [Python wrapper](https://pypi.org/project/glfw/) for the [GLFW](https://www.glfw.org/) library for setting up an GL canvas so Skia can draw on.

- [Poetry](https://github.com/python-poetry/poetry), easier to micro manage Python dependencies and generate builds.

### Python packages and others involved

- [SciPy](https://www.scipy.org/) and [NumPy](https://numpy.org/), the two must have packages on Python, very fast and flexible for scientific computing, lots of QOL functions.
  
  - Mainly used for calculating the FFTs and getting their frequencies domain representation.

- [audio2numpy](https://pypi.org/project/audio2numpy), [audioread](https://pypi.org/project/audioread), [soundfile](https://pypi.org/project/SoundFile) for reading an WAV, MP3, OGG and giving me the raw audio data.

- [mido](https://pypi.org/project/mido/) for reading MIDI files, transforming ticks to seconds and other utilities for the piano roll visualization.

- [OpenCV](https://opencv.org/) and [opencv-python](https://pypi.org/project/opencv-python/), for reading images of a video file without having to extract all of them in the start.

- [pip-chill](https://pypi.org/project/pip-chill/) for simplifying the `requirements.txt`.

- _Tom's Obvious, Minimal Language._: [Python interface](https://pypi.org/project/toml/), [main project](https://github.com/toml-lang/toml); _YAML Ain't Markup Language_: [Python interface](https://pypi.org/project/PyYAML/), [main project](https://yaml.org/): Both for reading / saving configuration files.
  
  - I dislike a bit JSON due to its kinda steep UX at first on fixing the syntax the end user itself, those two helps a lot on the overhaul UX on project I believe.

- The [Python Image Library](https://pypi.org/project/Pillow/) Pillow, was extensively used in the past as a render backend but now it is used only for rotating images then sending to Skia.

- Python package [samplerate](https://pypi.org/project/samplerate/) for a binding to libsamplerate, used for downsampling audio before calculating the FFT so we get more information on the lower frequencies.

- [requests](https://pypi.org/project/requests/). [tqdm](https://pypi.org/project/tqdm), [wget](https://pypi.org/project/wget), [pyunpack](https://pypi.org/project/pyunpack/), [patool](https://pypi.org/project/patool/) for fetching, downloading, showing progress bars and extracting External dependencies automatically for the users.

<hr>

_(There are missing Python dependencies here, mostly others that these packages depends on, but micro managing would be very hard)_

### Extras

The GNU/Linux operating system, contributors with code or money, every distribution I / you used, their package managers, developers, etc; For this amazing platform to develop on.

The platforms MMV code is hosted on.

The Open Source community.

