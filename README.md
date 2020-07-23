# Modular Music Visualizer

An attempt to make a free (as in freedom) and open source music visualization tool for the music production community

![Demo image of MMV](repo/demo.jpg)

[Link to unlisted video of the full music in the image above](https://youtu.be/BhpLwaR1Oj8)

_The DAW is Ardour 6.0_

# Idea

So I am a Free and Open Source music producer hobbyist that also happens to be a code hobbyist and at some point it's inevitable I'd be releasing my tracks to the internet and create some project to make the world a better place.

The problem is, I don't want to release a video of the track on a platform with a static image or just recording the screen nor pay for some software to generate an "music visualization" for me without much control of it.

So I searched up for a free (as in freedom and price) tool that does exactly that, they do exist but aren't as good as they could be, most of the time a bit basic..

Then I just got into this opportunity on making a suckless (as in quality not minimalism I see you lol) music visualization tool with the programming languages and tools I love and care.

# Table of contents

   * [Running](#running)
      * [Linux](#linux)
      * [Windows](#windows)
   * [Goals, what is being developed](#goals-what-is-being-developed)
   * [Contributing](#contributing)


# Wiki is TODO

Lot's of stuff are moving on the code and being rewritten, when things are more stable I'll write a proper guide.

Use the example scripts located on the project root folder as for now for learning and / or read the code, it's pretty well commented

# Running

Please, if you are running this project from source, after installing the Python dependencies install [pillow-simd](https://github.com/uploadcare/pillow-simd) instead of vanilla Pillow, preferably with the AVX2 instructions explained in its repo if your CPU supports so.

As you can see [here](https://python-pillow.org/pillow-perf/), `pillow-simd` is faster by a lot on imaging processing, it cut down render times with MMV from `2:34 minutes --> 1:89 minutes` and that was with `multiprocessed=False`, resize times went down from 34 seconds to only 13 not to mention faster GaussianBlurs.

#### IMPORTANT!!

If you're going to venture out on creating your own MMV scripts, I higly recommend reading the basics of Python [here](https://learnxinyminutes.com/docs/python/), it doesn't take much to read and will avoid some beginner pitfals.

Though you probably should be fine by just creating a copy of the example scripting I provide on the repo and reading through my comments and seeing the Python code working, it's pretty straightforward as I tried to simplify the syntax and naming functions with a more _"concrete"_ meaning. 

## Linux

Install Python and git on your distribution

- Arch / Arch based (Manjaro): `sudo pacman -Syu python git`

- Ubuntu / Debian based: `sudo apt install python git`

Open a shell on desired dir to clone the repo

`git clone https://github.com/Tremeschin/modular-music-visualizer`

`cd modular-music-visualizer`

[Use a Python venv](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs) (recommended):

- `python -m venv mmv-venv`

- `source ./mmv-venv/bin/activate`

`pip install -r mmv/requirements.txt`

Configure the stuff on the file `example.py`, run it with `python example.py`

I include a few free assets under the `assets/free_assets` folder, you can use them at your disposal, they were generated with my other project called [PyGradienter](https://github.com/Tremeschin/pygradienter) :)

## Windows

#### TL;DR good luck and feel free to ask for help or write me a proper guide on doing this

_Before starting, I wanted to point out that it might be possible for me to release a executable with all these dependencies but that kinda kills the modularity in the MMV name, and it would be preset-based until I find a better solution, feedback is really needed here as I don't have an easy Windows setup nor a license and I'm depending on some friends letting me control their pc remotely or asking instructions_

Running MMV on Windows is a bit troublesome, one of the things is because both the vector graphics API I use to transform vector graphics (SVG) to a PNG (RGBA array) to make the music bars [those are cairo and / or wand, both should work but cairo is preferred] works better under a Unix-like environment and are not as easy to install on Windows (by the look of things).

It's not much that following some instructions shouldn't do the trick, I'm just saying you would have a better time if running this under a Linux environment (you don't even have to install it to give a try, can be run off a USB stick!!)

I even had to revert the [ray](https://github.com/ray-project/ray) multiprocessing library I was using for scalability because it wasn't working and still under alpha stages on the Windows OS, so I switched back to Python's default multiprocessing library (the core code became a bit of a battle royale because of that but nevertheless it's not unstable).

I'm not completely sure but I think that cairosvg requires the Visual Studio Build Tools thingy, so [grab and install that](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

The `wand` rasterizer depends on the ImageMagick libraries, luckily they have a page on [on installing ImageMagick under Windows](http://docs.wand-py.org/en/latest/guide/install.html#install-imagemagick-on-windows)

Getting cairo to work can be painful as it seems, but I was able to find some resources on doing that. You don't install cairo directly but rather the GTK toolkit (a widget toolkit) as cairo directly depends on that.

The GTK project does have an official [install guide on Windows](https://www.gtk.org/docs/installations/windows/) as well as the [cairo people](https://www.cairographics.org/download/), but the cairo guide looks a bit outdated..

I've found this readthedocs page from the [weasyprint project](https://weasyprint.readthedocs.io/en/latest/install.html#windows) on installing GTK under Windows, it seems like the most complete guide out there.

[This repository](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) might help you out as well (probably solve everything beforehand?) so godspeed for you running Python 64 bit version!!

After all this trouble on installing two libraries that Linux users be like: _just_ `yay -S cairo imagemagick` _it!_, go ahead to [python.org](https://www.python.org/) and install Python 3.8 preferably the 64 bit version as GTK with 32 bit Windows seems outdated, be sure to check the box to add Python to the PATH variable on the installer otherwise you will not be able to quickly access Python through the command line!!

Now open a shell (shift + right click empty spot on the Windows folder manager, open PowerShell), download the source code on the repo main page or clone the repo with `git clone https://github.com/Tremeschin/modular-music-visualizer` (have git installed beforehand)

Preferably [Use a Python venv](https://github.com/Tremeschin/dandere2x-tremx/wiki/Python-venvs), not required but optimal

run `pip install -r mmv/requirements.txt` to install MMV's Python dependencies

#### I'd like some feedback if you could install everything fine and what you had to do to make it work :)

Configure the stuff on the file `example.py`, run it with `python example.py`

I include a few free assets under the `assets/free_assets` folder, you can use them at your disposal, they were generated with my other project called [PyGradienter](https://github.com/Tremeschin/pygradienter) that I'm merging the two here in MMV :)

# Goals, what is being developed

#### High priority / now

- [ ] (90%) Transforming PyGradienter into a Python package, merging the two repositories into one, making PyGradienter run on Windows and only returning the image array rather than saving on the disk

- [ ] (stuck) R&D alternative methods for converting SVG --> PNG under Python because Windows (or could someone write a small guide for installing cairo under Windows that works? I didn't put much effort until now on this)

- [ ] (half worked) R&D alternative methods for rendering the final frame (each branch is one way I tried _- and failed or wasn't really efficient_)

#### Medium priority

- [ ] Profile the code, find bottlenecks, general optimization on most expensive functions

- [ ] (boring) Update requirements.txt

- [x] ~~Make a proper presentation / demo / gif about MMV and link on README~~ didn't work well

#### Ideas for the future or waiting to be executed

- [ ] Progression bar (square, circle, pie graph?)

- [ ] Rectangle bars visualizer (only circle + linear or symetric currently)

- [ ] Rain images on pygradienter and rain particle generator?

# Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) file :)
