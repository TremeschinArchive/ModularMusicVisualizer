<p align="center">
    <img src="repo/mmv-project-logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  High quality video music visualization tool for the music production community.
  <br><hr>
  <i>Support for Music Bars and Piano Roll mode, Video as background, enable / disable whatever you want. Hack the code at your will. Custom GLSL shaders for post processing.</i>
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

![Demo image of MMV](repo/music-mode.jpg)
![Demo image of MMV](repo/music-mode-2.jpg)

[Link on YouTube](https://www.youtube.com/watch?v=5cUhRTab4Ks) (Music Bars Mode)

<hr>

![Demo image of MMV Piano Roll](repo/piano-roll-4.jpg)

[Link on YouTube](https://www.youtube.com/watch?v=NwP5LESrceY) (Piano Roll Mode)

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
   * [Hacking the Code](#hacking-the-code)
   * [Goals, what is being developed](#goals-what-is-being-developed)
   * [Contributing](#contributing)
   * [User Generated Content, legal](#user-generated-content-copyrighted-material-legal)
   * [Acknowledgements | Thanks to](#acknowledgements-thanks-to)

<hr>

# Community, Support, Help, Donations

I currently have a (very lonely) [Telegram group](https://t.me/modular_music_visualizer).

Feel free to enter and ask, share anything regarding the MMV project!!

I haven't yet made a decision on financial support, probably I'll have a donation option in the future, even though I dislike donationware as a developer working "full time" or "serious" on a project, I think it'll be the healthiest one for this project.

**Expect MMV to be forever Free (price and freedom).**

<hr>

# Running

Please see the file [docs/RUNNING.md](docs/RUNNING.md) for instructions on all platforms

<hr>

## Hacking the code

Want to understand how the code is structured so you can learn, modify, understand from it?

Please read [HACKING.md](docs/HACKING.md) file :)

Feel free DM me, I'd be happy to explain how MMV works.

# Goals, what is being developed

Also see [CHANGELOG.md](CHANGELOG.md) file :)

#### Next stuff

- [ ] Progression bar (square, circle, pie graph?)

- [ ] Implement text support (lyrics.. ?)

- [ ] Load and configure MMV based on a YAML file, so distributing binaries will be theoretically possible

- [ ] Generate rain droplets using shaders

#### Ideas for the future or waiting to be executed

- [ ] Rectangle bars visualizer (only circle + linear or symmetric currently)

#### Impossible / hard / dream

- [ ] Make MMV Piano Roll interactive for learning, writing midi files?

- [ ] (Help needed) Fully functional and configurable GUI

<hr>

# Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) file :)

This repository on GitHub is a mirror from the main development repository under [GitLab](https://gitlab.com/Tremeschin/modular-music-visualizer), I'm mostly experimenting with the other service.

I didn't set up bidirectional mirroring as that can cause troubles, GitLab automatically pushed every change I make to GitHub.

Feel free to create issues on any of both platforms, PRs / Merge Requests I ask you to do under GitLab (as I'm not sure what would happen if I accept something here? perhaps some protected branches shenanigans to solve this?).

<hr>

# User Generated Content, copyrighted material, legal

Any information, images, file names you configure manually is considered (by me) user generated content (UGC) and I take no responsibility for any violations you make on copyrighted images, musics or logos.

I give you a few "free assets" files, those, apart from the MMV logo I created myself on Inkscape, were generated with Python with some old code written by me, you can use them freely. Some are generated on the go if configured (they are on by default) on the running script of MMV.

# Acknowledgements, Thanks to

I want to show my gratitude to these projects, no joke, MMV wouldn't be possible if these projects didn't exist.

Those are not in order of importance at all, they are always used together.

I'll mainly list the main name and where to find more info, it's just impossible to list every contributor and person that took place into those.

### Main ones

- Python language (https://www.python.org), where development speed is also a feature.

- [Skia-Python wrapper](https://github.com/kyamagu/skia-python), for a stable Python interface with the [Skia Graphics Library](https://skia.org).
  
  - Generates the base videos and piano roll mode graphics.

- [ModernGL Python package](https://github.com/moderngl/moderngl) for making it simple to render fragment shaders at insane speeds under Python.
  
  - Also the ModernGL main developer [einarf](https://github.com/einarf) for helping me an substantial amount with some good practices and how to do's
  
- [FFmpeg, FFplay](https://ffmpeg.org), _"A complete, cross-platform solution to record, convert and stream audio and video."_ - and they are not lying!!

  - "The Only One". Transforms images into videos, adds sound, filters.

- The [GLSL](https://en.wikipedia.org/wiki/OpenGL_Shading_Language) language, OpenGL, Vulkan (on mpv flag), the [Khronos group](https://www.khronos.org) on its entirety, seriously, you guys are awesome!!

  - Also the [Python wrapper](https://pypi.org/project/glfw/) for the [GLFW](https://www.glfw.org/) library for setting up an GL canvas so Skia can draw on.

- [MPV](https://mpv.io), the best video player of all, `mpv --list-options | wc -l -> 1097`, near 1100 command line flags and options.
  
  - Used for applying specific post processing on videos and encoding them.
  - Might become deprecated code in the near future

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

