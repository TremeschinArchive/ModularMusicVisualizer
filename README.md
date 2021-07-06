# Modular Music Visualizer

**IMPORTANT NOTE:** For the "previous" and currently only working full featured code, [see this branch](https://github.com/Tremeschin/ModularMusicVisualizer/tree/master).


## Node Editor Branch

This branch is under heavy development!!

Plan on making MMV truly _modular_ and have an full featured GUI than script files for the end user. Much like Blender's Composite User Interface based on a Node Editor!!

Releases are now possible and builds work targeting:
- **Linux:** Uses AppImage, single binary.
- **Windows:** One compressed exe file.
- **MacOS:** Don't have the equipment to test.

All only include a single Data directory that stores default Shaders files, presets, fonts, images, nodes.

User directories are created on first execution such as Screenshots, Runtime (configs), Renders.

It auto downloads external dependencies in case you don't have them in system PATH (like FFmpeg both on Windows and Linux).

The shader render backend is called "Sombrero", I have to overhaul it a bit before rebasing into the GUI and this will take a while, but some of its features:
- **ShaderToy-inspired** variables, syntax
- **Camera2D** I give you the vectors. You do the math.
- **Camera3D** I give you the camera position and ray direction. You do the RayMarching.
- **Joystick** Control both Camera2D and Camera3D with a joystick, hot swap.
- **Multi Layer** Yeet as many shaders you want, alpha composite, chain shaders together.
- **Rendering Shaders to Video easily**


## Installing, running

### From Releases

Linux might need `fuse` installed for mounting the AppImage file. Windows should be a portable binary.

No releases are available for now since "nothing is working" regarding Shaders.

### From Source

Shortly, have Python 3.9 installed, download and extract the Source Code to some directory or git clone it, instructions below for Arch Linux: 

- `sudo pacman -Syu python ffmpeg python-poetry git`
- `git clone https://github.com/Tremeschin/ModularMusicVisualizer -b NodeEditor`
- `cd ModularMusicVisualizer`
- `poetry install --no-dev`
- `poetry run editor`

Should work on Windows with minimal changes, just install Python and `python.exe -m pip install poetry` and start from the `poetry install` command.
