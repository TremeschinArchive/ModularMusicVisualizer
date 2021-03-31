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
shadermaker = shadermaker(working_directory = working_directory, name = "Default MMV Preset")
BlockOfCode = shadermaker.block_of_code




# # Background

background = shadermaker.clone()
background.set_name("background-shader")


# Can put "shader" or "image"
BACKGROUND = "shader"
# BACKGROUND = "image"

if BACKGROUND == "shader":
    # Stars universe shader
    background.load_shader_from_path(
        path = f"{interface.shaders_dir}{sep}assets{sep}background{sep}stars.glsl",
        replaces = replaces,
    )
elif BACKGROUND == "image":
    # Map image, must be name="background"
    background.add_image_mapping(
        name = "background",
        path = f"{interface.MMV_PACKAGE_ROOT}{sep}assets{sep}free_assets{sep}glsl_default_background.jpg"
    )

    # Load moving image shader
    background.load_shader_from_path(
        path = f"{interface.shaders_dir}{sep}assets{sep}background{sep}moving_image.glsl",
        replaces = replaces,
    )

background.add_pipeline_texture_mapping(name = "mmv_fft", width = replaces["MMV_FFTSIZE"], height = 1, depth = 1)
background.build_final_shader()
background.save_shader_to_file(f"{interface.runtime_dir}{sep}{background.name}-frag.glsl")
background_path = background.get_path()



# # Logo, visualizer

logo_visualizer = shadermaker.clone()
logo_visualizer.set_name("music-bars-shader")
logo_visualizer.load_shader_from_path(
    path = f"{interface.shaders_dir}{sep}assets{sep}music_bars{sep}circle_sectors.glsl",
    replaces = replaces,
)
logo_visualizer.add_pipeline_texture_mapping(name = "mmv_fft", width = replaces["MMV_FFTSIZE"], height = 1, depth = 1)
logo_visualizer.add_image_mapping(name = "logo", path = f"{interface.MMV_PACKAGE_ROOT}{sep}..{sep}..{sep}repo{sep}mmv_logo_alt_white.png")
logo_visualizer.build_final_shader()
logo_visualizer.save_shader_to_file(f"{interface.runtime_dir}{sep}{logo_visualizer.name}-frag.glsl")
logo_visualizer_path = logo_visualizer.get_path()



# # # Main shader, alpha composite

master_shader = shadermaker.clone()
master_shader.set_name("default-master-shader")
master_shader.add_include("mmv_specification")
master_shader.add_dynamic_shader_mapping(name = "background", path = background_path)

# If you want to nullify some shader
if True:
    master_shader.add_dynamic_shader_mapping(name = "logo_visualizer", path = logo_visualizer_path)
else:
    master_shader.add_dynamic_shader_mapping(name = "logo_visualizer", path = NULL)

# Get texture from background and alpha composite
processing = shadermaker.transformations.get_texture(texture_name = "background", uv = "shadertoy_uv", assign_to_variable = "processing")
processing.extend(shadermaker.transformations.alpha_composite(new = "processing"))
master_shader.add_transformation(transformation = processing)

# Get texture from logo and alpha composite

processing = shadermaker.transformations.get_texture(texture_name = "logo_visualizer", uv = "shadertoy_uv", assign_to_variable = "processing")
processing.extend(shadermaker.transformations.alpha_composite(new = "processing"))
master_shader.add_transformation(transformation = processing)

# Gamma correction
master_shader.add_transformation(transformation = master_shader.transformations.gamma_correction())


# # Build shader, save 
master_shader.build_final_shader()
master_shader.save_shader_to_file(f"{interface.runtime_dir}{sep}{master_shader.name}-frag.glsl")
master_shader_path = master_shader.get_path()


# # Build custom include directories

coordinate_normalizations = shadermaker.clone()
coordinate_normalizations.set_name("coordinates_normalization")
coordinate_normalizations.load_shader_from_path(
    path = f"{interface.shaders_dir}{sep}include{sep}coordinates_normalization.glsl",
)
coordinate_normalizations.add_transformation(BlockOfCode(
"""
// Apply zoom in / out effect
float scale = 0.5 + ((atan(mmv_time * 2.0) / 3.1415) * 2) * 0.5;
if(scale < 0.99) {
    stuv *= scale;
    gluv *= scale;
    gluv_zoom_drag *= scale;
}
"""
))
coordinate_normalizations.build_final_shader()
coordinate_normalizations.save_shader_to_file(f"{interface.runtime_dir}{sep}{coordinate_normalizations.name}.glsl")


# Return info to the run shaders interface
global info
info = {
    "master_shader": master_shader_path,
    "include_directories": [interface.runtime_dir, "default"],
}