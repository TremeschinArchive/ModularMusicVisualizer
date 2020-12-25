This documentation needs some reviewing but should still be functional

# Running MMV on Windows

This project isn't extensively tested on Windows, feedback appreciated.

<hr>
<p align="center">
  <i>Prepare your disks and patience!!</i>
</p>
<hr>

Any easier steps for Windows are welcome specially for external installs other than Python that are needed.

**Chose:**

<hr>

##### 1. With Anaconda (less trouble)

Download and install `Anaconda` (not `miniconda`), make it your default Python optimally on the installer.

<hr>

##### 2. With vanilla Python (discouraged somehow)

Head over to [Python Releases for Windows](https://www.python.org/downloads/windows/), download a _"Windows x86-64 executable installer"_ (I currently use Python 3.8), install it (be sure to check _"ADD PYTHON TO PATH"_ option on the installer).

You'll also need to download `Build Tools for Visual Studio` which got merged into Visual Studio Community Edition, so search that (Build Tools for VS) and download the installer of the VS Community.

You'll need to install the whole C++ development package group so Python can use a compiler and the Windows SDK for building dependencies such as numpy. This will use quite a bit of disk space and definitely will take a while to complete. After that you can proceed to the next steps.

Search for `scipy` Python wheels and install the version listed on `requirements.txt`.

For this last step you can also manage to install lapack or blas / openblas on your system. I could not. This is finicky and I offer no official support for this.

<hr>

### Important: extra step for an automatic installation of dependencies

Go to [7-zip downloads](https://www.7-zip.org/download.html) website, download the `7-Zip for 64-bit Windows x64 (Intel 64 or AMD64)` executable if you don't have it already installed, run it and extract the files on the default path.


This step is required to extract the video encoder (FFmpeg) compressed files if you don't want to do this by hand.

<hr>

### Getting the source code

<hr>

**Chose:**

#### 1. GitHub / GitLab repository main page

You might be already here, head to the top page and there is a (green for GitHub, blue for GitLab) button _"⬇️ Code"_ and download as a ZIP.

Use a archive manager (something like 7-zip or rar) to extract the contents into a folder you'll be running MMV.

#### 2. Using git CLI

Install git  Windows the installer from [git downloads page](https://git-scm.com/downloads)

Open a shell on desired dir to clone the repo (GIT bash shell on Windows)

`git clone https://github.com/Tremeschin/modular-music-visualizer`

<hr>

### If running with Anaconda

Open the Anaconda shell from start menu, then we'll create an conda environment and activate it:

- `conda create --name mmv python=3.8`

- `conda activate mmv`

Now with basic CLI navigation commands, change to the directory you extracted or downloaded MMV, if it's on your Downloads folder, when executing the anaconda shell you should be at `C:\\users\your_user` so run:

- `cd .\Downloads\modular-music-visualizer-master\mmv`

Or just take the path on Windows Explorer and do:

- `cd "C:\\path\to\mmv\with\ugly\back\slashes"`

<hr>

### If running with vanilla Python

Open a shell on the downloaded and extracted folder

On Windows you can right click an empty spot on the Windows File Manager app while holding the shift key for a option to "Open PowerShell" here to appear.

Change the working directory of the shell to the folder `.\src` (or just execute the previous step on that folder which contains the file `base_video.py`)

This step is not required but good to do so, create an virtual environment (venv) and activate it:

- `python.exe -m venv mmv-venv`

- `.\venv-path\Scripts\activate.bat`

<hr>

**Chose:**

#### 1. Vanilla Python: automatic installation and running

When you run `python .\base_video.py --auto-deps` it should take care of downloading and installing Python dependencies as well as FFmpeg, mpv and musescore as needed by working on the externals folders, moving the binary to the right place.

If you're on anaconda, perhaps running with `--user` as so: `python .\base_video.py --auto-deps --user` should fix permission errors.

If this process doesn't work (dead links for example), report any issue you had. You can also continue reading this for manual instructions.

<hr>

#### 2. Vanilla Python: manual FFmpeg and Python deps installation

Download a compiled FFmpeg [build](https://ffmpeg.org/download.html#build-windows), the binary named `ffmpeg.exe` must be on the directory `ROOT/mmv_skia/mmv/externals/ffmpeg.exe`.

Install Python dependencies with `pip install -r .\mmv\requirements.txt`

Run MMV with `python .\base_video.py`

<hr>
<p align="center">
  <i>Either by following path 1 or 2 you should have your final default video on the `renders` folder after running `base_video.py` script.</i>
</p>
<hr>

# Post processing

You can't render videos out of this but only visualize real time

Edit the file `post_processing.py` then run it. Don't set a target output video, comment the line by adding a # at the beginning.

Head back to the original [RUNNING.md](RUNNING.md) for instructions on configuring your own stuff
