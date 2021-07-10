<p align="center">
    <img src="App/mmv/Data/Image/mmvLogoWhite.png" alt="Modular Music Visualizer Project Logo" width="200" height="200">
</p>
<h3 align="center"><b>Modular Music Visualizer</b></h3>
<p align="center">
  <i>The Interactive Shader Renderer Platform.</i>
</p>
<hr>


**IMPORTANT NOTE:** _For the "previous" and currently only working full featured code, [see this other branch](https://github.com/Tremeschin/ModularMusicVisualizer/tree/master)._

<hr>


An <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/opensource.svg" style="vertical-align: middle;" width="23"> Open Source shader rendered platform written in <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/python.svg" style="vertical-align: middle;" width="23"> Python, capable of reacting in real time to audio playing on the computer or rendering to video files.





# Node Editor Branch

This branch is under heavy development, keep reading for new features and changes, where this is heading, running instructions. 



# New Features

## Node Editor

Plan on making MMV truly _modular_ and have an full featured GUI than script files for the end user.

Much like Blender's Composite User Interface based on a Node Editor!!

Also save, load presets, so community work, sharing session files will be possible without much trouble compared to before.

<hr>

## Releases

Releases are now possible and builds work targeting:
- **Linux:** Uses AppImage, single binary.
- **Windows:** One compressed exe file.
- MacOS: Don't have the equipment to test.

All only include a single Data directory that stores default Shaders files, presets, fonts, images, nodes.

User directories are created on first execution such as Screenshots, Runtime (configs), Renders.

It auto downloads external dependencies in case you don't have them in system PATH (like FFmpeg both on Windows and Linux).

<hr>

## Translations

Yes! Translations are possible now, any contribution is welcome for helping accessibility for everyone.

_The percentages of translations are shown on the GUI itself by clicking the bottom left Language button selector._

**>> Status of translations**:

> Main languages
- <div>
    <img src="https://hatscripts.github.io/circle-flags/flags/us.svg" style="vertical-align: middle;" width="24">
    <span style="vertical-align: middle;">(English) Defaults to English if don't know the translation.</span>
</div>

- <div>
    <img src="https://hatscripts.github.io/circle-flags/flags/br.svg" style="vertical-align: middle;" width="24">
    <span style="vertical-align: middle;">(Brazilian Portuguese) My native language, translations will be near 100% all time.</span>
</div>

> Proof of Concept
- <div>
    <img src="https://hatscripts.github.io/circle-flags/flags/jp.svg" style="vertical-align: middle;" width="24">
    <span style="vertical-align: middle;">(Japanese) Using different fonts as needed, extended unicode ranges thingy.</span>
</div>




_Thanks for [HatScripts](https://github.com/HatScripts/circle-flags) for the flags icons used here and on releases!!_

<hr>

## Better Shader Render Backend

The shader render backend is called "Sombrero", I have to overhaul it a bit before rebasing into the GUI and this will take a while, but some of its features:
- **ShaderToy-inspired** variables, syntax
- **Camera2D** I give you the vectors. You do the math.
- **Camera3D** I give you the camera position and ray direction. You do the RayMarching.
- **Joystick** Control both Camera2D and Camera3D with a joystick, hot swap.
- **Multi Layer** Yeet as many shaders you want, alpha composite, chain shaders together.
- **Rendering Shaders to Video easily**, react to audio or not.



<hr>

# Installing, running

<div align="center">
  <b>Running From Releases</b>
</div>

Linux might need `fuse` installed for mounting the AppImage file. Windows should be a portable binary.

No releases are available for now since "nothing is working" regarding Shaders or the final product.

<hr>

<div align="center">
  <b>Running Directly from Source Code</b>
</div>


<hr>
<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  
  GNU/Linux 
</div>
<p>

- <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/arch_linux.svg" style="vertical-align: middle;" width="32">`$ sudo pacman -Syu python ffmpeg python-poetry git`

- <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/ubuntu.svg" style="vertical-align: middle;" width="32"> `$ sudo apt update && sudo apt upgrade && sudo apt install python3 ffmpeg python3-poetry git`

- `git clone https://github.com/Tremeschin/ModularMusicVisualizer -b NodeEditor`
- `cd ModularMusicVisualizer`
- `poetry install`
- `poetry run editor`



<hr>
<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="64"> 
  
  Windows (7+)
</div>
<p>

- Install [latest stable release Python "Windows installer (64-bit)"](https://www.python.org/downloads/windows/), be sure to check `Add Python 3.X to PATH`.
- Download Modular Music Visualizer's [Source Code](https://github.com/Tremeschin/ModularMusicVisualizer/archive/refs/heads/NodeEditor.zip), extract to somewhere.
- `Shift + Right Click` empty spot on a empty spot on the extracted folder in Windows Explorer (file manager), click `Open PowerShell Here`.
- Install poetry with: (command can also be found [here](https://github.com/python-poetry/poetry#windows-powershell-install-instructions))
  - `(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python.exe -`
- Run: `python.exe -m poetry install`
- Run: `python.exe -m poetry run editor`


<hr>
<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="64">
  
  macOS
</div>
<p>

- Install [Homebrew](https://brew.sh/), _"The Missing Package Manager for macOS"_
- `brew install python@3.x ffmpeg python`
- `python3 -m pip install poetry`
- `git clone https://github.com/Tremeschin/ModularMusicVisualizer -b NodeEditor`
- `cd ModularMusicVisualizer`
- `poetry install`
- `poetry run editor`



<hr>

# Community, links, help

Check out our:

- <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/telegram.svg" style="vertical-align: middle;" width="24"> [Telegram Channel](https://t.me/modular_music_visualizer)
- <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/github.svg" style="vertical-align: middle;" width="24"> [GitHub](https://github.com/Tremeschin/ModularMusicVisualizer)


<hr>

# License

The Modular Music Visualizer Python code I have written are GPLv3 Licensed, some snippets can be CC or MIT but I always mark and give proper attribution when that happens.

**Shader Files**: I might MIT them in the future (the whole thing won't work great outside MMV anyways), for now I'll let you use parts of it if you need, attribution required.

**Fonts** licenses have their own (`FontName License.md`) together with their file.

**MMV Logo**, I won't be mad if you use it but let's keep it as a "MMV Project" property, it's just there so one can recognize the software a bit better and / or have a default logo image on the visualization bars. Since the project is always evolving, having old videos with the logo doesn't feel optimal because quality on mainstream is usually ahead of the time.


# Attribution, thanks to

**Attributions are not required** but would show **gratitude** for the project!!


## Thanks to

These are not in any order of more important or less important, all have their own crucial role in MMV.

It is quite impossible to list everyone, so check `pyproject.toml` for the full list, also some packages depends on others and there are usually multiple contributors to every single one of those.

### Python Packages:
- [DearPyGui](https://github.com/hoffstadt/DearPyGui): Awesome GUIs easily.
- [Nuitka](https://github.com/Nuitka/Nuitka): Great Python bundling package, great final AppImage on Linux, very compressed binaries on Windows.
  - [PyInstaller](https://github.com/pyinstaller/pyinstaller/) is good as well but always unpacking the final binary to a temp dir then running is a bit :/ for the disk and startup times.
- [ModernGL](https://github.com/moderngl/moderngl): Great OpenGL Python bindings.
  - [GLFW](https://www.glfw.org/) is used for the window, great cross platform OpenGL Contexts.
  - Shout out to [einarf](https://github.com/einarf) for helping me with ModernGL
- [NumPy](https://numpy.org/): Gotta love NumPy arrays and the speed on computations.
  - [NumPy Quaternions](https://github.com/moble/quaternion): Quaternions support in NumPy, great 3D rotations than [Euler Angles](https://github.com/moble/quaternion/wiki/Euler-angles-are-horrible).
- [DotMap](https://github.com/drgrib/dotmap): Really great "dynamic" dictionaries
- [tqdm](https://github.com/tqdm/tqdm): Gotta love easy status bar.
- [mido](https://pypi.org/project/mido/): Reading MIDI files
- [Poetry](https://github.com/python-poetry/poetry): Less instructions on README for creating, enabling virtual environments for Python, lots of high level commands for facilitating the end user.
- [OpenCV](https://opencv.org/) and [opencv-python](https://pypi.org/project/opencv-python/) for reading frames from videos individually.

### Externals / Third Party:
- [FFmpeg](https://ffmpeg.org/): Do I have to say something? _"A complete, cross-platform solution to record, convert and stream audio and video."_ - and they are not lying!!
