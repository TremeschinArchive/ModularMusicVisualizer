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

- **Simply a full featured music visualization software.**

<p>

- **No watermark, pay walls or any crap.**

<p>

- **Everything available at no cost.**

<p>

- **Everything configurable.**

<hr>
Officially works on Linux, macOS and Windows, high chance of working *BSD
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

Currently there are two "versions" of the Modular Music Visualizer project on this repository, one uses the Skia drawing library and the other uses GLSL shaders, the first one currently aimed at rendering the piano roll and music visualization bars mode and the second one while I hope some day will replace the first one it currently works as a post processing layer.

Sadly due to factors outside my control (I use the `mpv` program as the backend) applying post processing and rendering to videos only works on Linux (and probably macOS, *BSD) operating systems (see [this comment](https://github.com/mpv-player/mpv/issues/7193#issuecomment-559898238)), Windows users will only be able to apply the post effects real time but not get an easy file out of the code. It's possible to record the screen though at severe costs of quality. If you're on Windows you CAN render to videos, only MMVSkia that is which is the base of the 

- **Basic navigation**: You'll mainly need to use basic command line interface and navigation such as `cd` (change directory), `mkdir` (make directory), `pwd` (print working directory). Don't be afraid of searching how those work on Windows because I am very rusty on its CLI. On the other OSs, most should be POSIX compliant and literally use the same command.

<p>

- **Windows Note**: You might need to replace `python` with `python.exe` if using PowerShell (recommended) or CMD (I'm not completely sure btw).

<p>

- **Windows Note**: Another point is that directories on Windows uses `\` instead of (what everything else uses) `/`, Python should convert those automatically, however the shell (where you call commands) might not convert those like `.\path\to\executable.exe` instead of `./path/to/executable.exe`, the second one might not run on Windows. This does not apply on the Python scripts as it'll auto convert `/` to `\\`.

### Running MMV Skia

Please see the file [mmv_skia/README.md](mmv_skia/README.md) for instructions

### Running MMV GLSL Shaders

Please see the file [mmv_shader/README.md](mmv_shader/README.md) for instructions

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

<hr>

# Honest word

Don't abuse from your freedom the power to ascend with this software with much hard work put on it.

Pay back your fees with a simple **"Thank you"** at least.

It doesn't seem much but pursuing something others also keep an expectancy or genuinely changed their lifes for good is a hell of a great motivation: **being awknowledged not for feeling superior or meaningless better, but for being helpful, making a diference, gratitude.**

*Don't take this as an obligation, you're free, this software is free.*

The Modular Music Visualizer project definitely changed my life, I grew up so much as a programmer, my problem solving skills accuracy and speed improved a lot, not to mention general organization of stuff.. I'm already victorious on the existence and execution of such code.

Can't forget to **thank a lot all the people behind all the dependencies I used in this project**. We don't need to come up with pythagoras theorem from scratch anymore as someone did that for us in the past. Just like I don't need to make an complex video encoder, there's the FFmpeg team already. Old generations making a better world and time for future ones.

<hr>

# Thank You

My sincere Thank You if you read the README all the way until here, hopefully you learned something new and that this project helped you!!

<hr>

