This documentation needs some reviewing but should still be functional

# Running MMV on MacOS // Help needed

I am very inexperienced with macOS but here's the steps I had to do for getting MMV up and *(half)* running:

- Install `homebrew`, I don't know how often people do this or even use it.. but it's a package manager and should make stuff easier.
  
  - Go to https://brew.sh/ and run their command on *"Install Homebrew"* section

  This should take a while since it requires that Xcode CLI thing where it is not small.

- After it's installed, run `brew install ffmpeg python` to install Python (3.8 was what I got) and FFmpeg (the video encoder)

I already had `git` so just do:

- `git clone https://github.com/Tremeschin/modular-music-visualizer`

- `cd ./modular-music-visualizer/src`

Then run `python3 base_video.py --auto-deps --user`

If you want it automatically to convert `MIDI -> audio` please also run `brew install fluidsynth --with-libsndfile`

I did get a few OpenGL errors when doing this as I was using a mac VM with the scripts of this repo: https://github.com/foxlet/macOS-Simple-KVM

**Disclaimer:** I just installed the system for testing my code, I won't use any products I don't own there, I just want to support many platforms as possible. This was the cheap and dirty solution of it I was sure I'd get a few errors there, but most stuff went fine.

Feedback wanted on native macOS, this is as far as I can help you for now. I can say one friend of mine could run and it worked, however he had to downgrade to Python 3.8 under homebrew.

Head back to the original [RUNNING.md](RUNNING.md) for instructions on configuring your own stuff
