<p align="center">
    <img src="repo/mmv_logo.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center">Modular Music Visualizer</h3>
<p align="center">
  High quality video music visualization tool for the music production community.
  <br><hr>
  <i>Real Time mode for live DJing, Support for Music Bars and Piano Roll mode, Video as background, enable / disable whatever you want. Hack the code at your will.</i>
</p>
<hr>

- **Simply a full featured music visualization software.**

<p>

- **Everything available at no cost.**

<p>

- **Everything configurable.**

<p>

- **No watermark, pay walls.**

<p>

- **Real time.**

<hr>
Officially works on Linux with all features, most work on macOS and Windows
<hr>


# Sombero Branch

Basically rewriting the whole project with tech and previous knowledge.

Be patient, this will take a few but stuff is going very smooth.

Upcoming: Camera 2D, 3D, joystick support, proper piano roll support.







# Legal, User Generated Content, copyrighted material, warranty

I'm no lawyer so this is general advise to protect myself and you, users:

Any information, images, videos, file names you configure is considered user generated content (UGC) and I take no responsibility for any violations you make on copyrighted images, musics or logos. For example, if you generate some video with a copyrighted music using MMV and upload that, get some flag or strike I take absolutely no responsibility on your action.

## License

Currently all™ the (main) files of this repository are licensed under the GPLv3 license, some functions are Creative Commons (CC) and I kept those attributed with the original creator or where I learned core concepts from, so check every file beforehand.

I might use the MIT license on GLSL shaders files in the future, depends on my will (I'm currently 35% favorable of this idea), though those are ultra specific to MMV's interface and processing so what's the point to MIT if it's about sharing knowledge and GPLv3 does that?

### Trademark

I don't really feel like legally registering trademarks for MMV's logo or name since it's mostly an basic image and name so one can recognize more easily the project, but I consider the MMV logo and the name "Modular Music Visualizer" to be project-related "trademarks".

Since I, Tremeschin, am the original creator and current only main developer, I feel like having this governance on top of those two original ideas is totally understandable from the end user's point of view, keeping them on my control.

This doesn't mean you can't use MMV logo on video releases, in fact I came up with it so at least you have something there in the middle, I just ask to reference the project if you're using that image.






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

  - Also the [Python wrapper](https://pypi.org/project/glfw/) for the [GLFW](https://www.glfw.org/) library for setting up an GL stuff.

- [Poetry](https://github.com/python-poetry/poetry), easier to micro manage Python dependencies and generate builds.

### Python packages and others involved

- [SciPy](https://www.scipy.org/) and [NumPy](https://numpy.org/), the two must have packages on Python, very fast and flexible for scientific computing, lots of QOL functions.
  
  - Mainly used for calculating the FFTs and getting their frequencies domain representation.

- [audio2numpy](https://pypi.org/project/audio2numpy), [audioread](https://pypi.org/project/audioread), [soundfile](https://pypi.org/project/SoundFile) for reading an WAV, MP3, OGG and giving me the raw audio data.

- [mido](https://pypi.org/project/mido/) for reading MIDI files, transforming ticks to seconds and other utilities for the piano roll visualization.

- [OpenCV](https://opencv.org/) and [opencv-python](https://pypi.org/project/opencv-python/), for reading images of a video file without having to extract all of them in the start.

- _Tom's Obvious, Minimal Language._: [Python interface](https://pypi.org/project/toml/), [main project](https://github.com/toml-lang/toml); _YAML Ain't Markup Language_: [Python interface](https://pypi.org/project/PyYAML/), [main project](https://yaml.org/): Both for reading / saving configuration files.
  
  - I dislike a bit JSON due to its kinda steep UX at first on fixing the syntax the end user itself, those two helps a lot on the overhaul UX on project I believe.

- Python package [samplerate](https://pypi.org/project/samplerate/) for a binding to libsamplerate, used for downsampling audio before calculating the FFT so we get more information on the lower frequencies.

- [requests](https://pypi.org/project/requests/). [tqdm](https://pypi.org/project/tqdm), [wget](https://pypi.org/project/wget), [pyunpack](https://pypi.org/project/pyunpack/), [patool](https://pypi.org/project/patool/) for fetching, downloading, showing progress bars and extracting External dependencies automatically for the users.

<hr>

_(There are missing Python dependencies here, mostly others that these packages depends on, but micro managing would be very hard)_

### Extras

The GNU/Linux operating system, contributors with code or money, every distribution I / you used, their package managers, developers, etc; For this amazing platform to develop on.

The platforms MMV code is hosted on.

The Open Source community.

<hr>



