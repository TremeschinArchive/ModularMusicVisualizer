## [2.5.1] :: Optimize :: (2020-12-28)
- Don't calculate FFT for the mono channel
- Overhaul shave some extra 10% speed on rendering times
- Remove some deprecated code
- Add logging timings on MMVImage
- Add customizable encoding settings
- Failsafe for reading audio
- Use raw FFmpeg binary for piping videos into (shave ffmpeg-python dependency)

## [2.5.0] :: Unite :: (2020-12-25)
- Merge both MMVSkia and MMVShader into a "common interface package", this allows:
  - Sharing common files between the two
  - General modularity and easiness of implementing new stuff having their own namespace (kinda)
- Split documentation into `RUNNING{_ON_LINUX,_ON_MACOS,_ON_WINDOWS,_TLDR,}`
- Replace midi2audio with Musescore for converting midi -> audio (higher quality and it doesn't trim the start!!)

## [2.4.0] :: Boring :: (2020-12-22)
- Start to replace every print() function with proper logging.....
- Also commenting stuff
- Pass argument depth for every function so we have the call stack on the logging as well

## [2.3.5] :: Headache :: (2020-11-07)
- ~~Add option for automatically converting `MIDI -> Audio`, downloads FreePats General MIDI sound set, check their license at http://freepats.zenvoid.org/licenses.html before using.~~ deprecated, see version [2.5.0]
- New default demo sample sound, WIP kawaii bass
- Code doesn't run if not Python >= 3.9 (`skia-python` packages not available for 3.9)
- Experimental GLSL shader rendering to image and video
- Rename mmv to mmv_skia, add experimental mmv_shader files

## [2.3.4] :: Cleanup, textures, Windows QOL :: (2020-11-07)
- Add basic GUI file on experiments.py
- Unify stuff on experiments.py
- Delete old pygradienter code, rewriting
- Add `bar_magnitude_multiplier` on MMVMusicBarCircle option
- Add `audio_amplitude_multiplier` option
- Generate backgrounds on the go before an run, no need to keep them on repo
- Auto download, extract, add to PATH FFmpeg binaries on Windows
- Windows fixes throughout the code
- Test MMV code on Ubuntu, Fedora, Manjaro, OpenSUSE Tumbleweed, macOS, Windows 10
- Heavy README review, formatting

## [2.3.3.3] :: Minor :: (2020-10-20)
- Add `maximum_bar_size` to MMVSkiaMusicBarsCircle, hard limits the bar sizes relative to the minimum size (starting point)
- Progression bar now accepts `shake_scalar`, offsets out-of-the-window direction by audio amplitude times this scalar, 0 for piano roll, 14 for mode music
- Optimizations: remove avoiding quick math calculation and getting values from stored dict (what I was thinking lol?)

## [2.3.3.2] :: Verbose Logging :: (2020-10-10)
- Add `bar_starts_from` in MMVSkiaMusicBarsCircle, "last" and "center" starting positions
- Verbose MMVMusicBarCircle
- Verbose configuration phase on `mmv.__init__.py`
- Show updated biases on MMVContext
- Rename preset_musical_notes to preset_balanced
- More verbose MMVSkiaCore
  
## [2.3.3] :: Simplifications :: (2020-10-07)

- Minor performance improvement, remove unnecessary list comprehension on MMVSkiaCore
- Get the old `fftinfo` and `this_step` by attributes on MMVCore, so from anywhere just `self.mmv.core.modulators` or `self.mmv.core.this_step`
- Rename every instance of Number to float, as float includes integers (technically)
- *MASSIVE*, **MASSIVE**, **M A S S I V E** rewrite and overhaul of `mmv_image_configure.py`
- Accelerate particles speed on audio average amplitude for preset middle out

## [2.3.2] :: Quality of Life :: (2020-10-06)

- Start organizing music bars circle kwargs for custom shiny stuff
- Comment `mmv_music_bar_circle.py`, add configs options on `mmv_music_bar.py`
- Add `bigger_bars_on_magnitude` for MMVSkiaMusicBarsCircle and its scalar
- Start to overhaul generators, preset bottom mid up and middle out
- Fix bar colors (weird having to reset the path to apply a new paint)
- Create and link official Telegram group for MMV
- Implement configurable particle directory for generators
- Remove deprecated attributes on context, `make_directory_if_doesnt_exist` utility on end user `mmv` class
- Save video renders to a `RENDER_DIR` on `example_basic.py`
- More configurable Fade properties on particles
- Make logo and music bars 5% smaller
- Image logo more responsive than music bars resize, nice "popping" effect

## [2.3.1] :: Quality of Life :: (2020-10-03)

Start to write changelogs (probably should've started early on the project)
 
- Fix music bars small gap at the top (theta=90°) and doubled (stacked) bars on bottom (theta=-90°)
- Fix Remaining Approach interpolation to scale on any FPS (generators don't yet, last thing TODO)

(Past recent stuff)

- Add customizable colors on Piano Roll mode
- Massive overhaul on `example_basic.py`, greatly improve UX
  - Ability to easily switch between Music and Piano Roll mode
  - Add `THIS_FILE_DIR` for absolute referring to relative files according to the example script
  - Comment what the end user should be aware of when using a feature
- Add `HACKING.md` for a quick guide on the structure code of MMV
- Fix wrong pixel format on Skia Canvas to image array on Windows OS
- Fix wrong bars channels (they were swapped, L on R side of screen, R on L)
- Better current status, show in minutes:seconds, keep updating single line
- Performance improvement, no dictionaries on binned FFTs
- Better automatic video file name, adds fps, mode, audio filename