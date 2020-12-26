
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

# Running

- **Basic navigation**: You'll mainly need to use basic command line interface and navigation such as `cd` (change directory), `mkdir` (make directory), `pwd` (print working directory). Don't be afraid of searching how those work on Windows because I am very rusty on its CLI. On the other OSs, most should be POSIX compliant and literally use the same command.

Currently there are two "versions" of the Modular Music Visualizer project on this repository, one uses the Skia drawing library and the other uses GLSL shaders.

The first one (Skia) is currently aimed at rendering the piano roll and music visualization bars mode.

The second one (Shaders / GLSL) while I hope some day will replace the first one (it's a lot faster) it currently works as a post processing **extra** layer.

Every end user script is located under the first directory after the `/src/` folder, namely `base_video.py` and `post_processing.py`.

As said previously, base video is MMVSkia and post processing is MMVShader

<hr>

#### Important NOTE for Windows and macOS users

Sadly due to factors outside my control (I use the `mpv` program as the backend) applying post processing **AND RENDERING TO A FILE** only works on **Linux** operating systems (see [this comment](https://github.com/mpv-player/mpv/issues/7193#issuecomment-559898238))

**Windows and macOS** users **CAN** and **HAVE THE FULL FUNCTIONALITY OF MMV SKIA** available, only video with shaders applied won't be possible **rendering to files, viewing realtime is possible**.

For a better visualization, please refer to this next table **SPECIFIC FOR MMV SKIA**:

| Base MMV + Configuration script | Rendering to Video |
|---------------------------------|--------------------|
| Linux                           | V                  |
| Windows                         | V                  |
| macOS                           | V                  |

It's possible to record the screen of the video with shaders applied running at severe costs of quality in the case of MMV GLSL shaders and non Linux platform.

For a better visualization, please refer to this next table **SPECIFIC FOR MMV GLSL**:

| Video + GLSL Shaders | Viewing Realtime | Rendering to Video |
|----------------------|------------------|--------------------|
| Linux                | V                | V                  |
| Windows              | V                | X                  |
| macOS                | V                | X                  |




## Getting the source code

Either go to the main repository page located at [GitHub](https://github.com/Tremeschin/modular-music-visualizer) or [GitLab](https://gitlab.com/Tremeschin/modular-music-visualizer), find the download button button (Down Arrow Code usually), or..

Alternatively install GitHub Command Line Interface (or git from your Linux distro / MacOS Homebrew) and run:

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

# Editing your configs

You can read through the scripts located

<hr>

# Instructions per platform

Also see [EXTRAS.md](EXTRAS.md) file for squeezing some extra performance.

## Linux

Please see file [RUNNING_ON_LINUX.md](RUNNING_ON_LINUX.md)

## Windows

Please see file [RUNNING_ON_WINDOWS.md](RUNNING_ON_WINDOWS.md)

## MacOS

Please see file [RUNNING_ON_MACOS.md](RUNNING_ON_MACOS.md)

<hr>

## Editing configs

Pass flag `mode=music` or `mode=piano` for a quick swap between the two: `python base_video.py --auto-deps mode=[music,piano]`. (mode=music is already implied and default)

Everything I considered useful for the end user is under `base_video.py` controlled by upper case vars such as `INPUT_AUDIO`, `MODE`, `OUTPUT_VIDEO`, etc.

Change those or keep reading the file for extra configurations.

Can also configure first then run `python post_processing.py` for applying some shaders to the output (mpv dependency required), only limitation is that Windows users can't render to a file but are allowed to see the result in real time.

If you're going to venture out on creating your own MMV scripts or hacking the code, making new presets, I highly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfalls.

Though you probably should be fine by just creating a copy of the example scripting I provide on the repo and reading through my comments and seeing the Python code working, it's pretty straightforward the top most abstracted methods as I tried to simplify the syntax and naming functions with a more _"concrete"_ meaning. 

At one point I'll have a proper wiki on every argument we can send to MMV objects.
