"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Default configuration for MMV, this file uses shader maker and yields
some.

The variables in this scope will be exactly the ones where this function is
called from, see run_shaders.py .__load_preset()

Yes, Python linting will be quite annoyed here...

You can edit this file and see changes after saving and pressing "r" on MMV
shader window!

===============================================================================
"""
import os

# pylint: disable=E0602

# # # Initialize shader maker
shadermaker = shadermaker(working_directory = working_directory, replaces = replaces)
macros = shadermaker.macros
BlockOfCode = shadermaker.block_of_code


# # Build custom include directories

coordinate_normalizations = macros.load(path = interface.shaders_dir / "include" / "coordinates_normalization.glsl")

# Start zoom in then zoom out
coordinate_normalizations.add_transformation(BlockOfCode(
"""
// Apply zoom in / out effect
float scale = 0.5 + ((atan(mmv_time * 2.0) / 3.1415) * 2) * 0.5;
if(scale < 0.99) {
    stuv *= scale;
    gluv *= scale;
    gluv_all *= scale;
    stuv_all *= scale;
}
"""
))
# Append prefix=false for stuff loaded on "include" is optimal
coordinate_normalizations.finish(append_prefix = False)


# # Background

background = shadermaker.clone()

# Some background presets for you
# BACKGROUND = "stars"
# BACKGROUND = "image"
BACKGROUND = "blueprint"

if BACKGROUND == "universe":

    # Stars universe shader
    background.load_shader_from_path(
        path = interface.shaders_dir / "assets" / "background" / "stars.glsl",
        replaces = replaces,
    )

elif BACKGROUND == "blueprint":
    background.load_shader_from_path(path = interface.shaders_dir / "assets" / "background" / "blueprint.glsl")

elif BACKGROUND == "image":
    # Map image, must be name="background"
    background.add_image_mapping(
        name = "background",
        path = interface.MMV_PACKAGE_ROOT / "assets" / "free_assets" / "glsl_default_background.jpg",
    )

    # Load moving image shader
    background.load_shader_from_path(
        path = interface.shaders_dir / "assets" / "background" / "moving_image.glsl",
        replaces = replaces,
    )



# # Logo, visualizer

logo_visualizer = macros.load(path = interface.shaders_dir / "assets" / "music_bars" / "circle_sectors.glsl")
logo_visualizer.add_pipeline_texture_mapping(name = "mmv_radial_fft", width = replaces["MMV_FFTSIZE"], height = 1, depth = 1)
logo_visualizer.add_image_mapping(name = "logo", path = interface.MMV_PACKAGE_ROOT/".."/".."/"repo"/"mmv_logo_alt_white.png")

# Want some chromatic aberration on logo?
if True:
    chromatic_aberration = macros.load(path = interface.shaders_dir / "assets" / "pfx" / "chromatic_aberration.glsl")
    logo_visualizer = macros.chain(A = logo_visualizer, B = chromatic_aberration)



horizontal_bars = macros.load(path = interface.shaders_dir / "assets" / "music_bars" / "horizontal.glsl")
horizontal_bars.add_pipeline_texture_mapping(name = "mmv_linear_fft", width = replaces["MMV_FFTSIZE"], height = 1, depth = 1)


# PFX

vignetting = macros.load(path = interface.shaders_dir / "assets" / "pfx" / "vignetting.glsl")


# Waveform

waveform = shadermaker.clone()
waveform.load_shader_from_path(path = interface.shaders_dir / "assets" / "dev" / "waveform.glsl")
waveform.add_pipeline_texture_mapping(
    name = "mmv_waveform", width = replaces["WAVEFORM_LENGTH"], height = 1, depth = 2,
    repeat_x = False, repeat_y = False, mipmaps = False, anisotropy = 1
)
chromatic_aberration = macros.load(path = interface.shaders_dir / "assets" / "pfx" / "chromatic_aberration.glsl")
waveform = macros.chain(A = waveform, B = chromatic_aberration)


# # # Master shader, alpha composite

master_shader = shadermaker.clone()

layers = [
    background,
    waveform,
    horizontal_bars,
    logo_visualizer,
]

# Rain effect
if BACKGROUND in ["image", "blueprint"]:
    rain = macros.load(path = interface.shaders_dir / "assets" / "fx" / "rain.glsl")
    layers.append(rain)

layers.append(vignetting)

# # Alpha composite
master_shader = macros.alpha_composite(layers = layers)

# Gamma correction and finish
master_shader.add_transformation(transformation = master_shader.transformations.fade_in())
master_shader.add_transformation(transformation = master_shader.transformations.gamma_correction())
master_shader_path = master_shader.finish()



# Return info to the run shaders interface
global info
info = {
    "master_shader": master_shader_path,
    "include_directories": [interface.runtime_dir, "default"],
}