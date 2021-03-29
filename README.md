<p align="center">
    <img src="repo/mmv_logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  High quality video music visualization tool for the music production community.
  <br><hr>
  <i>Support for Music Bars and Piano Roll mode, Video as background, enable / disable whatever you want. Hack the code at your will. Real Time mode for live DJing and some extra modes</i>
</p>
<hr>

- **Simply a full featured music visualization software.**

<p>

- **No watermark, pay walls or any crap.**

<p>

- **Everything available at no cost.**

<p>

- **Everything configurable.**

<p>

- **Real time.**

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

# How MMV Works

In short, take a look at the diagram:

![MMV Diagram](https://tremeschin.gitlab.io/mmv/how-mmv-works.png)

<hr>

_^(I used icons from the [Papirus Icon Theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), credits to their respective authors, we share the same license of code. I'm displaying a diagram (made with [Diagrams dot Net](https://app.diagrams.net/), [Repository](https://github.com/jgraph/drawio)) not a software though, have not modified their icons)_

<hr>

Here's some insights, technical difficulties I had to overcome:

### 1. Inputs / Outputs, feature detection

As you can see we **must have some audio source** let it be **real time playback** or an original audio file or **MIDI file** that [MuseScore](https://github.com/musescore/MuseScore) converted to audio.

We then **slice the audio** into many **chunks** and calculate a series of features, one of them is the [Fourier Transform](https://www.youtube.com/watch?v=spUNpyF58BY) which gives us the **frequency spectrum of the audio**.

<hr>

### 2. Generating Video

After that it's just a matter of implementation of Computer Generated Imagery **(CGI)** utilizing (in the _"new" code of dynamic bars_) the **OpenGL Shading Language (GLSL)** for instructions how and where to render stuff, sending the images to [FFmpeg](https://ffmpeg.org/) and generating a final video as fast as possible or simply render to the screen on the real time mode _(yields fastest performance)_.

<hr>

### 3. GPU, Shaders

This GLSL part is a bit complicated since there is the `MMVShaderMGL` **wrapper I wrote for displaying shaders which includes a basic preprocessor for mapping images, videos and even other shaders as textures** (images on the GPU), recursively. This makes it possible to **separate into many layers** and apply **individual** effects and transformations on them.

It uses the [ModernGL Python package](https://github.com/moderngl/moderngl) for communicating with GL, also **translating from ShaderToy to MMVShaderMGL is very straightforward** just by replacing some variable names and removing some parts. *This also will become a full featured wrapper in the near future™*

**MMV Can also be described as a more robust alternative to ShaderToy with quite some extra flexibility and options, parameters to tinker with.**

Just a quick disclaimer, I'm relatively new to coding Shaders and C-like languages, optimizations, don't expect good fps on a < budged system.

### 4. Memory usage

Apart from textures we must send to the GPU, audio buffers, FFT calculations many projects regarding audio in Python reads **the whole uncompressed content** in a single go using one of the many packages that does this.

This means we load **all the raw data of the audio on the memory** and potentially be get some Out of Memory error.

Since I can see people using MMV for rendering 1h, 2h long videos of music mix, long piano compositions, even podcasts, I spent some time making **FFmpeg yield these raw bytes of the audio** stream for me, using a Python subprocess.

Since subprocesses have a limited buffer size determined by your OS, when this gets full it'll just wait until we use that data, **this way we're progressively reading a raw audio stream from file and don't have to use 4 GB of ram per 30m audio** file~.

In the end, MMV doesn't abuse the ram that much, though rendering in 1080p+ resolutions FFmpeg's x264 encoder will tend to use quite some juicy ram, so be careful. Also VRAM on resolutions higher than 4k can be spicy.

<hr>

# Community, Support, Help, Donations

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer working "full time" or "serious" on a project, I think it'll be the healthiest one for this project.

**Expect MMV to be forever Free (price and freedom).**

Please be patient if you want features to be implemented, I work on MMV code in my spare time, college been quite exhausting lately.

<hr>

# Running

**Important: The project is under some heavy rewiring and R&D, have yet to normalize instructions and documentation, I can't test everything after every commit so expect minor bugs.** Also there is technically two projects in the same repository ("old" MMVSkia and new MMVShader) sharing some common files, keeping compatibility while rewriting stuff is a bit tricky and is the main source of current problems.

## Python

Please install Python 64 bits (hard requirements are _V >= 3.7_).

It is preferred to use Python 3.8 but it should work on later versions.

**Python must be a 64 bits installation**, also **Only a 64 bits OS will work**. If you're on Windows you can just open a shell and type `python.exe`, see if you get win32 or not on the info, or just try running MMV code, it'll auto detect.

The easiest way to run MMV is by using an alternative community Python "package manager" called [Poetry](https://github.com/python-poetry/poetry), it automatically will create environments (containers) for MMV's dependencies and install it for you.

Alternatively you can chose not to use poetry but the regular `requirements.txt` of Python.

First you have to install Python:

<hr>

### Installing Python

_Linux and macOS have optional dependency `musescore` to convert midi files to audio when using Skia + Piano Roll mode_

**Windows Note:** Windows uses ugly backslashes `\` rather than forward slashes `/` when referring to files and directories. Replace those to yours equivalent OS separator.

<hr>

- **Windows:** Head over to [Python dot org](https://www.python.org/downloads/windows/), download **Python 3.X.X Windows x86-64 executable installer**, install it and make sure to **check the box "Add Python 3.X.X to PATH"** and you are getting a **64 bits, x86-64 version**. Version 3.8 or 3.9 is preferred.

<hr>

- **Linux:** Install Python and other deps from your package manager (`ffmpeg, musescore`), for example:
  - *Arch Linux, Manjaro, pacman-based:* `sudo pacman -Syu base-devel git ffmpeg python musescore`
  - *Ubuntu:* `sudo apt update && sudo apt upgrade && sudo apt install python3 python3-venv python3-dev python3-setuptools python3-pip ffmpeg git libglfw3 libglfw3-dev build-essential`

Only FFmpeg is required for rendering.

<hr>

- **macOS:** I don't have the hardware to test nor proper knowledge but should be something like:
  - Install [Homebrew](https://brew.sh/)
  - `brew install python ffmpeg musescore git`

<hr>

### Installing Poetry

Follow instructions on [Poetry's README](https://github.com/python-poetry/poetry#installation) or install from your package manager.

For Pacman you probably can run `sudo pacman -Syu python-poetry`

On **Windows** I think it's easier to run `python.exe -m pip install poetry --user` on PowerShell or Command Prompt rather than their curl script or cloning the repo, I had no issues running MMV there with this.

### Getting the Source Code of MMV

Either go to the main repository page at [GitHub](https://github.com/Tremeschin/modular-music-visualizer), click the green down arrow saying "Code", extract to somewhere

Or just `git clone https://github.com/Tremeschin/modular-music-visualizer` if you have GIT command line interface.

### Installing Dependencies

Open a shell on the folder where you extracted MMV (shift + right click empty space on Windows, _"Open PowerShell here"_), Linux and macOS users should be able to change the working directory into the folder (basic shell navigation) or by right clicking your file manager (at least Nautilus, Dolphin with extension)

If you're executing with plain Python I suggest you to create a virtualenv and activate it then install requirements `pip install -r ./requirements.txt`. I prefer Poetry so this is out of the scope:

Run:

- `poetry install`

_(Binary is `poetry.exe` on Windows if you're on PowerShell or just `poetry` if on old Command Prompt)_

## Actually Running

I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfalls.

For the "new" code (shaders), keep reading.

For the "old" code, configure the file `/src/run_skia.py` to your needs (images, audios) _[though there is a default configuration, if you want fast results skip this]_ before continuing, though it have some defaults so you can get some out of the box experience

### Executing:

<hr>

#### Running Skia "old" code

Quick Skia code tutorial, for shaders ignore this part:

- `poetry run skia`: "Old code", music mode -> video file
- `poetry run skia mode=piano`: "Old code", piano roll mode -> video file
- `python ./src/run_skia.py (arguments)`

Edit this `run_skia.py` with some config. This is "deprecated" code, will be kept for historical reasons.

<hr>

#### Running Shaders code

- `poetry run shaders (arguments)`
- `python ./src/run_shaders.py (arguments)`

For the Shaders arguments, keep reading, they are kinda complex.

# Configuration Flags

These apply only to the Shaders interface, since the Skia code is being "replaced".

You can run `poetry run shaders --help` and see a list of possible commands and arguments.

You can and probably want to chain these commands, just be sure to run the `render` or `realtime` ones in the end otherwise you'll execute in the wrong order.


### Width, height, fps

For extra info, example:

- `poetry run shaders --resolution help`
- `poetry run shaders --resolution --width 1920 --height 1080 --fps 60`


### Supersampling Anti Aliasing (SSAA), Multi Sampling Anti Aliasing (MSAA)

For extra info, example:

- `poetry run shaders antialiasing --help`
- `poetry run shaders antialiasing --ssaa=1.5 --msaa 8`

SSAA internally renders the video at a X times higher resolution than the target output, then downscales to the desired resolution.

This prevents jagged edges and makes the video more smooth at the cost of about (`2^SSAA`) times less performance, so `SSAA=2` is 4x more render time, `SSAA=4` is 8x, `SSAA=8` is 16x, `SSAA=1.5` is 2.25x.

Optimally use 2 for final exports (maybe not for target output 4k unless you have a beefy GPU)


### Preset

You can pass the `preset` command and set a target name:

- `poetry run shaders preset --name "default"`

It looks for files under `/src/mmv/shaders/presets/{NAME}.py` and executes them for generating the shaders and run them.

It's quite hard to explain with text how they work so check out the file itself so you can make your own or change some configuration.

You can press `r` key on live mode to reload them, no need to quit and come back, more on this later.


### "Multiplier"

Multiply audio amplitudes and frequency values (realtime or not) by this scalar (yields more aggressiveness)

`poetry run shaders multiplier --value 2.5`


### (Real Time mode) Get recordable devices

- `poetry run shaders list-captures`

Will give you a list of indexes of the captures you can use


### (Real Time mode) Visualize

After configuration,

- `poetry run shaders realtime --help`
  
Example:

- `poetry run shaders realtime`
- `poetry run shaders realtime --cap N`
- `poetry run shaders multiplier --value 2.0 realtime`
- `poetry run shaders multiplier --value 2.0 preset --name "other_preset" realtime`

There are a couple hotkeys and interactions with the window:

- Can click + drag to translate space, scroll to zoom in / out
- Shift + scroll increases / decrease the intensity of effects (multiplier)
- Ctrl + scroll increases / decrease the SSAA (Super Sampling Anti Aliasing), gets exponentially slower to render but gives nicer edges as explained, also might leak some ram so better quit and set another target SSAA from scratch.
- Pressing `z` resets zoom back to 1x
- Pressing `x` resets dragged space back to the origin
- Pressing `i` resets the intensity to 1
- Pressing `r` rebuilds the preset and reloads the shaders
- Pressing `s` freezes the pipeline so the shader is rendered (hopefully) static, useful for debugging or screenshots
- Pressing `t` resets time to 0 (same as restarting MMV)

And of course, all of those are smoothly animated, not too quick nor too slow, but snappy.

### Rendering

Docs:

- `poetry run shaders render --help`

Example:

- `poetry run shaders render --audio "/path/to/audio.ogg"`
- `poetry run shaders render --audio "/path/to/audio.ogg" --output-video "this_video_contributed_to_global_warming_and_the_heat_death_of_the_universe.mp4"`
  
<hr>




## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

Feel free DM me, I'd be happy to explain how MMV works.

# Performance

I was able to sustain even 144 fps on my mid level hardware of 2019, running Jack Audio on Linux with 128, 256, 512 samples of audio buffer, though I'd recommend 256 or 512 just in case we miss some data.

It highly depends on the settings you use like resolution, target fps and the audio processing's batch size, but it was more than enough for live DJing while having a full DAW playing audio in the background.

I'm quite new to GLSL programming and my shaders can definitely be improved at least 4x more speeds and efficiency, but oh well GPUs are damm fast.

Also my audio processing processes stuff with `BATCH_SIZE = 2048 * 4` at about 230 FPS on my CPU, so we're technically limited by this when rendering plus your GPUs raw compute power, memory bus transfer speeds.

It definitely saturates my CPU with the video encoder (if I'm not SSAAing and have lots of movement on the screen), 100% constant usage.

# Goals, next idea

- [x] MMVShaderMaker: Basic version working!!

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

Don't advertise MMV's logo as "I made it"-content, I don't really feel like legally registering trademarks and whatnot since it's mostly an basic logo for the project so one can recognize it more easily.

# Acknowledgements, Thanks to

I want to show my gratitude to these projects, no joke, MMV wouldn't be possible if these projects didn't exist.

Those are not in order of importance at all, they are always used together, though they do follow some order of importance.

I'll mainly list the main name and where to find more info, it's just impossible to list every contributor and person that took place into those.

### Main ones

- Python language (https://www.python.org), where development speed is also a feature.

- [ModernGL Python package](https://github.com/moderngl/moderngl) for making it simple to render fragment shaders at insane speeds under Python.
  
  - Also the ModernGL (current?) main developer [einarf](https://github.com/einarf) for helping me an substantial amount with some good practices and how to do's
  
- [FFmpeg, FFplay](https://ffmpeg.org), _"A complete, cross-platform solution to record, convert and stream audio and video."_ - and they are not lying!!

  - "The Only One". Transforms images into videos, adds sound, filters.

- The [GLSL](https://en.wikipedia.org/wiki/OpenGL_Shading_Language) language, OpenGL, Vulkan (on mpv flag), the [Khronos group](https://www.khronos.org) on its entirety, seriously, you guys are awesome!!

  - Also the [Python wrapper](https://pypi.org/project/glfw/) for the [GLFW](https://www.glfw.org/) library for setting up an GL canvas so Skia can draw on.

- [Poetry](https://github.com/python-poetry/poetry), easier to micro manage Python dependencies and generate builds.

- [MuseScore](https://github.com/musescore/MuseScore), a really good composition software with a very promising next major release, really good default soundfont and CLI for converting midi to audio files. 

- [Skia-Python wrapper](https://github.com/kyamagu/skia-python), for a stable Python interface with the [Skia Graphics Library](https://skia.org).
  
  - Generates the base videos and piano roll mode graphics.

### Python packages and others involved

- [SciPy](https://www.scipy.org/) and [NumPy](https://numpy.org/), the two must have packages on Python, very fast and flexible for scientific computing, lots of QOL functions.
  
  - Mainly used for calculating the FFTs and getting their frequencies domain representation.

- [audio2numpy](https://pypi.org/project/audio2numpy), [audioread](https://pypi.org/project/audioread), [soundfile](https://pypi.org/project/SoundFile) for reading an WAV, MP3, OGG and giving me the raw audio data.

- [mido](https://pypi.org/project/mido/) for reading MIDI files, transforming ticks to seconds and other utilities for the piano roll visualization.

- [OpenCV](https://opencv.org/) and [opencv-python](https://pypi.org/project/opencv-python/), for reading images of a video file without having to extract all of them in the start.

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










# Extra Modes

MMV, apart from music visualization, is capable of doing some other neat things still about audiovisual content processing.

## JumpCutter mode

Following [carykh's](https://github.com/carykh) original idea of the project [JumpCutter](https://github.com/carykh/jumpcutter) and given that it looks half abandoned with yet some remaining activity on some community around it, I decided to implement myself this code in MMV because most of required stuff were already there.

This implementation have some advantages over the original one:

- **1.** It does not write frames to disk, making disk usage virtually almost as low as we can get.
- **2.** It renders pretty fast, I have processed 1h20m 720p24 content cut down to 55m in just about 12 minutes on my CPU.
- **3.** Reads audio progressively, no need to dump the full audio into memory in the start, so RAM usage is about as low as it'll get.

However for the time being it lacks some precision syncing, also real time mode is TODO, feels very doable.

### Running JumpCutter mode

Run with setting the input and outputs with:

- `poetry run jumpcutter (inputs, flags)`

For both modes you have some common flags:

- `threshold=float` The threshold to silence in audio amplitude normalized from 0 to 1. Default value is `0.015`.
- `sounded=float` The sounded speed, defaults to 1.
- `silent=float` The silent speed, defaults to 10.
- `o="path.extension"` What file to output the final result. Be careful to output videos to valid video formats and audio to valid formats.
- `batch=int` In how many blocks of size N we cut the audio? Based on the sample rate, defaults to 4096. Don't use values too much low `<512`, not only it'll sound bad but take more time to process.

JumpCutter will imply what to render based on what inputs you give, setting an automatic output format `ofmt`:

- Only inputting video assumes `ofmt=video`, uses audio from the video.
- Only inputting audio assumes `ofmt=audio`.
- Inputting both video and audio will use the two combined on `ofmt=video`.

Note: sending `ofmt={audio,video}` manually overrides the guessing of MMV's part.

However, manually setting some video and audio as input with output format to audio will simply ignore the audio you send.

There are two modes, one is to listen real time and other to render to file. It defaults to "render":

- `mode=render`, `mode=view`. TODO: implement real time visualization for JumpCutter

For `mode=view` you can pass `poetry run jumpcutter list` to see the list of outputs if it uses the wrong one.

Most flags differ for the two modes for outputs:

#### Video mode: (ofmt=video)
  
- `video="some video.mkv"` The target video to process.
- `audio="some audio.ogg"` The target audio to process.
- `w=1280 h=720` Sets the render resolution (scaled relative to original video).
- `m=0.5` Multiplies the original resolution by this factor and overrides width and height (`w` and `h`).

#### Audio mode: (ofmt=audio)

You can also only process a given audio from a video or a file. Simply send:

- `audio="path to audio"`

Or alternatively

- `video="some video" ofmt=audio`

#### Example usage

- `poetry run jumpcutter video="video.mkv" o="output.mkv"` _"Default mode"_
- `poetry run jumpcutter video="video.mkv" m=0.5 o="output.mkv"` _"Fast mode, render half the resolution, degrates a lot in quality"_
- `poetry run jumpcutter video="video.mkv" w=1280 h=720 o="output.mkv"` _"Render in 720p"_
- `poetry run jumpcutter video="video.mkv" threshold=0.03 o="output.mkv"` _"Consider values up to 0.03 silent"_
- `poetry run jumpcutter video="video.mkv" silent=200 sounded=1.3 o="output.mkv"` _"Faster than usual"_
- `poetry run jumpcutter video="video.mkv" silent=1 sounded=200 o="output.mkv"` _"?????????"_
- `poetry run jumpcutter audio="some audio.ogg" o="output.mp3"` _"Process only this audio"_
- `poetry run jumpcutter video="video.mkv" ofmt=audio o="output.flac"` _"Process only the audio of the video"_

<hr>





