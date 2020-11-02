## [2.3.4] :: Cleanup, textures, Windows QOL :: Ongoing development
- Add basic GUI file on experiments.py
- Unify stuff on experiments.py
- Delete old pygradienter code, rewriting
- Add `bar_magnitude_multiplier` on MMVMusicBarCircle option
- Add `audio_amplitude_multiplier` option
- Generate backgrounds on the go before an run, no need to keep them on repo
- Auto download, extract, add to PATH FFmpeg binaries on Windows
- Windows fixes throughout the code

## [2.3.3.3] :: Minor :: (2020-10-20)
- Add `maximum_bar_size` to MMVMusicBarsCircle, hard limits the bar sizes relative to the minimum size (starting point)
- Progression bar now accepts `shake_scalar`, offsets out-of-the-window direction by audio amplitude times this scalar, 0 for piano roll, 14 for mode music
- Optimizations: remove avoiding quick math calculation and getting values from stored dict (what I was thinking lol?)

## [2.3.3.2] :: Verbose Logging :: (2020-10-10)
- Add `bar_starts_from` in MMVMusicBarsCircle, "last" and "center" starting positions
- Verbose MMVMusicBarCircle
- Verbose configuration phase on `mmv.__init__.py`
- Show updated biases on MMVContext
- Rename preset_musical_notes to preset_balanced
- More verbose MMVCore
  
## [2.3.3] :: Simplifications :: (2020-10-07)

- Minor performance improvement, remove unnecessary list comprehension on MMVCore
- Get the old `fftinfo` and `this_step` by attributes on MMVCore, so from anywhere just `self.mmv.core.modulators` or `self.mmv.core.this_step`
- Rename every instance of Number to float, as float includes integers (technically)
- *MASSIVE*, **MASSIVE**, **M A S S I V E** rewrite and overhaul of `mmv_image_configure.py`
- Accelerate particles speed on audio average amplitude for preset middle out

## [2.3.2] :: Quality of Life :: (2020-10-06)

- Start organizing music bars circle kwargs for custom shiny stuff
- Comment `mmv_music_bar_circle.py`, add configs options on `mmv_music_bar.py`
- Add `bigger_bars_on_magnitude` for MMVMusicBarsCircle and its scalar
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