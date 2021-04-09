"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Render shaders to video files or preview them realtime, map images,
videos and even other shaders as textures into a main one, all recursively.
Also a basic preprocessor for including contents of other shader.

The shader interface you always needed.

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

# # # DOCUMENTATION

"""
# # # # # # Talk is cheap show me the code

import time
import mmv

# Get interfaces
interface = mmv.MMVPackageInterface()

# Boot MMVShaderMGL
mgl = interface.get_mmv_shader_mgl()(master_shader = True)

# Add some Include dir
mgl.include_dir(f"{interface.shaders_dir}{os.path.sep}include")

# # Render settings

mgl.target_render_settings(
    width = 1920,
    height = 1080,
    ssaa = 1,
    fps = 60,
)

mgl.mode(
    window_class = "glfw",
    strict = False,
    vsync = False,
    msaa = 4,
)

# Load shader from path
mgl.load_shader_from_path(path)

# Vsync loop, call .next() and .update_window()
while True:

    # When we started so we vsync
    start = time.time()

    # Next methods
    mgl.next()
    mgl.update_window()

    # Should we stop
    if mgl.window_handlers.window_should_close:
        break

    # Manual vsync
    while (time.time() - start) < (1 / 60):
        time.sleep(1 / (60 * 100))

# That's all, well, for visualizing simple shaders with access to the preprocessor,
# for audio stuff you gotta run through run_shaders.py it's more complicated

# # # # # # Description

    This file is intended to interface with moderngl Python package and provide
some bindings, utilities, a basic preprocessor, shortcuts for mapping images, videos,
pipelines, uniform values, deals with creating textures, window, contexts, rendering,
outputting, giving you a set of utilities for making sound interactive shaders.

    This also automatically includes some MMV specification at the start of the file
so some variable names are reserved or already defined, see below the list.

# # # # # # Usage

Within MMV the expected way is this:

| import mmv
| interface = mmv.MMVPackageInterface()
| mgl = interface.get_mgl_interface(master_shader = True)

This is the same as importing MMVShaderMGL directly from this file.
Also note that (master_shader = True) is expected to be given because that's the guy
who deals with the window and outputting to the screen's resolution, etc.

After that it is expected to be run:

| mgl.target_render_settings(
|     width = WIDTH,
|     height = HEIGHT,
|     ssaa = SUPERSAMPLING,
|     fps = FRAMERATE,
| )

So we have information on how to render.

Width and height will only be fixed size if rendering headless mode or strict mode.
SSAA renders at a higher internal resolution and outputs to screen / renders to file
at the target. Real time window mode width's and height's will be overridden when the
window is resized if strict mode is False otherwise kept the same. More in a few.

You probably want to specify some include directories for the preprocessor to find

| mgl.include_dir(GLSL_INCLUDE_FOLDER)

Where GLSL_INCLUDE_FOLDER is a path on the system, preferably use absolute pathing.

Now we set the "mode" to render, this differs from "quality" which target_render_settings
kind of deals with.

| mgl.mode(
|     window_class = "headless",
|     strict = True,
|     vsync = False,
|     msaa = MSAA,
| )

- window_class: can be "glfw", "pyglet", "headless", etc, see moderngl_window docs. Preferred is GLFW
- strict: Strict mode means to not by any means change the target width and height, render
    at fixed resolution. Forced in headless mode just in case.
- vsync: Wait for buffer swap of the window
    NOTE: IMPORTANT: this heavily degrades MMV multithreaded code performance for some reason
        please write your own vsync if displaying real time. This is implemented on run_shaders.py
    For render mode, vsync = False is preferred so we harvest all we can.
- msaa: Number of multi sampling anti aliasing to use. Shouldn't take much impact on
    performance since MMV doesn't yet works with many geometry

After that you're supposed to loader some master shader from path that renders the final
images only.

| mgl.load_shader_from_path(
|     fragment_shader_path,
|     vertex_shader_path = MMV_MGL_DEFAULT_VERTEX_SHADER, 
| )

# # # # # # Preprocessor

This is the heart of why this file is so big. The general syntax is:
- //#mmv {dictionary}

The easiest and simplest one is:
    - //#mmv {"type": "name", "value": NAME_OF_THIS_SHADER}

The next one is:
    - //#mmv {"type": "include", "value": "coordinates_normalization"}
    - //#mmv {"type": "include", "value": "/path/to/glsl.glsl"}

    Name is the name (without the .glsl) of some file in the included directories.
    For example, if your directory have like:
    
    | include
    | | file1.glsl
    | | file2.glsl

    And you set value to "file1" it'll include the contents of the [file1.glsl]
    based on a mode.

    Mode can be one of the two:

    - multiple: Allow re-including, examples are:
        - [math_constants.glsl]
        - [coordinates_normalization.glsl]

    - once: Only ever include once this file in THIS loaded GLSL. Best example is
        including [mmv_specification.glsl] on the beginning of the file.

    - //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    - //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "once"}

    It defaults to "multiple".

    This is for avoiding redefining values and functions, for that I advise also not
    to shadow variables, and use stuff like [math_constants.glsl] on the beginning of
    functions where you'll immediately use them. Not recommended using multiple if 
    you're defining functionality or some common variables names

The main (and most complex) mapping is this one:
    - //#mmv {
        "type": "map", "name": name of variables,
        "loader": [image, video, shader, dynshader, pipeline_texture],
        "value": path,
        "width": int, "height": int, (not for dynshader)
        "depth": int, (pipeline_texture only)
    }

    We load some loader with the value interpreted accordingly.
    Width, height and depth not always will be used.

    For all loaders it'll add these variables on the code:
        - sampler2D with name [name], the texture to read from
        - vec2 with name [name]_resolution storing the width and height
        - int with name [name]_width storing the width
        - int with name [name]_height storing the height

    Here's the info on each loader:

    - loader=image:
        This loads some raw contents of a image on the system given by its path
        stored on the [value]. Will get the read image's resolution

    - loader=video: (see *1. below)
        This gets one cv2.VideoCapture of a video on the system given by its path
        stored on the [value]

    - loader=shader: (see *1. below)
        This recursively generates other MMVShaderMGL classes and loads the shader
        on the system given by its path stored on the [value].
        
        This works by creating one FBO and Texture attached to one another so whatever
        we render to the FBO can be accessed on that texture in this OpenGL context
        and, since we share the context, we can use the contents of other shaders.
        
        The pipeline of information is also recursively sent from the master shader,
        the one which is called for the final render, recursively.

        Every other #pragma map on child shaders also works, mapping a video on shader1
        to the screen, applying blur on some other shader1 which have some map like: 
        #pragma map layer1=shader;shader1_path
        then pass this intermediate shader2 which modifies shader1 to some other shader3
        which deals with alpha compositing or something.

    - loader=dynshader:
        I called this "dynamic shader", it DOES NOT REQUIRE WIDTH AND HEIGHT and its 
        textures and target renderers will be dropped and recreated to always match
        the window's or internal width and height resolution.

    - loader=pipeline_texture:
        This creates a empty texture with a certain width, height and depth you can
        write to give by its name. We have this special function:
        
        - mgl.write_texture_pipeline(texture_name = "fft", data = FFT_DATA)
        
        Which finds this texture by name and write some data to it.
        It is good to use this method for communicating big arrays of data between
        Python and the OpenGL stuff.

    (*1.) You are required to pass a width and height for the shape you want the image
        it is not automatically got because we might want to stretch to some specific
        proportion. Does not require depth argument, all are treated as RGBA (vec4)

For getting images out of the window we have two functions:

| mgl.read_into_subprocess_stdin(target)
| mgl.read()

The first one accepts a Python's subprocess.Popen stdin with subprocess.PIPE as a target
and directly writes the value to the stdin (of FFmpeg generally speaking).

The second one gets you the raw data of the window buffer (headless or not).

They should output rgb24 values (RGB, 1 byte = 8 bits each) at the current target width
and height, so please use headless for rendering and be sure to match the width, height,
set FFmpeg's pixel format to rgb24 accepting from a pipe (-i -)

For the MMV specification, what they do, default variables and pipelines keep reading
this file.
"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Default shader vertex, just accepts an input position, places itself relative to the
# XY plane of the screen and gives us back an uv for the fragment shader
MMV_MGL_DEFAULT_VERTEX_SHADER = """\
#version 330

// Input and Output of coordinates
in vec2 in_pos;
in vec2 in_opengl_uv;
in vec2 in_shadertoy_uv;

// Raw UV coordinates outputs
out vec2 opengl_uv;
out vec2 shadertoy_uv;

// Main function, only assign the position to itself and set the uv coordinate
void main() {
    // Position of the vertex on the screen
    gl_Position = vec4(in_pos, 0.0, 1.0);
    
    // The raw uv from opengl and shadertoy coordinate mappings
    opengl_uv = in_opengl_uv;
    shadertoy_uv = in_shadertoy_uv;
}"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# MMV Specification
# We prefix every fragment shader with this, it's the declaration of uniforms and whatnot
# we also modify, add to it custom ones the user chose.
MMV_MGL_FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX = """\
    
// ===============================================================================

/// [Prefix] MMV MGL Shader Prefix

#version 330

// // Input and Output of coordinates, colors

// Raw UV coordinates inputs
in vec2 opengl_uv;
in vec2 shadertoy_uv;

// Color output 
out vec4 fragColor;

// // MMV Specification

uniform int mmv_frame;
uniform float mmv_time;
uniform vec2 mmv_resolution;

uniform float mmv_rotation;
uniform float mmv_zoom;
uniform vec2 mmv_drag;
uniform int mmv_flip;

// Gui
uniform bool is_dragging;
uniform bool is_gui_visible;
uniform bool mmv_debug_mode;

// Keys
uniform bool mmv_key_shift;
uniform bool mmv_key_ctrl;
uniform bool mmv_key_alt;

// Progressive audio amplitude
uniform vec3 mmv_progressive_rms;

//#shadermgl add_uniforms

// ===============================================================================

"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Transparent, black shader, used for ignoring a certain layer quickly
# Usage:
# | #pragma map some_other_unwanted_shader=dynshader;MMV_MGL_NULL_FRAGMENT_SHADER
# | ... GLSL code
MMV_MGL_NULL_FRAGMENT_SHADER = "void main() { fragColor = vec4(0.0); }"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# If shader compilation fails, fall back to this
MMV_MGL_FALLBACK_MISSING_TEXTURE_SHADER = f"""
// ===============================================================================

// This is the fallback shader when something went wrong, check console output
// for errors as well as the log of the faulty shader.

// ===============================================================================

{MMV_MGL_FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX}

// Decide if this uv is magenta or not
bool is_magenta(vec2 uv) {{
    uv = floor(uv);
    if (mod(uv.x + uv.y, 2.0) == 0.0) {{
        return true;
    }} else {{
        return false;
    }}
}}

void main() {{
    // Get coord with aspect ratio
    vec2 stuv = shadertoy_uv;
    stuv.x *= (mmv_resolution.x / mmv_resolution.y);

    // Transpose
    stuv += vec2(mmv_time / 64.0, mmv_time / 64.0);

    // Empty col
    vec4 col = vec4(0.0);
    
    // Grid
    float size = 16.0;
    
    // Raw resolution to uv normalized based on grid size
    vec2 pixel = 6.0 / mmv_resolution;

    // Kernel size 5
    for (int x = -5; x < 5; x++) {{
        for (int y = -5; y < 5; y++) {{

            // Where to put black or that magenta
            if (is_magenta(size * stuv + dot(pixel, vec2(x, y))) ) {{

                // Add color divided by kernel area and decrease when away from center
                col += (vec4(1.0, 0.0, 1.0, 0.5) / 25.0) * (1.0 - sqrt(x*x + y*y) / 5.0);
            }}
        }}
    }}

    fragColor = col;
}}
"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# When an uniform is not used it doesn't get initialized on the program
# so we .get(name, FakeUniform()) so we don't get errors here
class FakeUniform:
    value = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # Imports

from mmv.mmvshader.mmv_shader_mgl_window_handlers import MMVShaderMGLWindowHandlers
from mmv.mmvshader.mmv_shader_mgl_preprocessor import MMVShaderMGLPreprocessor
import mmv.common.cmn_any_logger
from pathlib import Path
from array import array
import numpy as np
import subprocess
import moderngl
import tempfile
import logging
import shutil
import time
import uuid
import sys
import gc
import os

class MMVShaderMGL:
    EXPERIMENTAL_VIDEO_MIPMAP = True
    DEVELOPER_RAM_PROFILE = False
    DEVELOPER = False

    # # Window management, contexts

    # Configurate how we'll output the shader
    def target_render_settings(self, width, height, fps, ssaa = 1, verbose = False):
        debug_prefix = "[MMVShaderMGL.target_render_settings]"
        (self.width, self.height, self.fps, self.ssaa) = (width, height, fps, ssaa)
        self.original_width, self.original_height = width, height
        if verbose: logging.info(f"{debug_prefix} Render configuration is [width={self.width}] [height=[{self.height}] [fps=[{self.fps}] [ssaa={self.ssaa}]")

    def set_reset_function(self, obj): self.__reset_function = obj
    def dummy(self): pass

    # # Apart from these last functions other end user expected functions see end of this class

    # # Generic methods

    def __init__(self, flip = False, master_shader = False, gl_context = None, screenshots_dir = None):
        debug_prefix = "[MMVShaderMGL.__init__]"
        self.master_shader = master_shader

        # Screenshot dir only up to master shader
        if self.master_shader:

            # No given path
            if screenshots_dir is None:
                screenshots_dir = Path(tempfile.tempdir())
                logging.info(f"{debug_prefix} Getting temp dir for screenshots")

            # Enforce pathlib.Path
            if isinstance(screenshots_dir, str): screenshots_dir = Path(screenshots_dir)

            # Assign
            self.screenshots_dir = screenshots_dir
            logging.info(f"{debug_prefix} Screenshots dir is [{self.screenshots_dir}]")

        # Name
        if self.master_shader:
            self.name = "Master Shader"
        else:
            self.name = str(uuid.uuid4())

        # Config
        self.flip = flip
        self.ssaa = 1

        # If you want to have some reset function to be called before reading shaders from path again
        # namely updating ShaderMaker
        self.__reset_function = self.dummy

        # Will be True if user presses "r" key, expected someone outside this class to revert to False
        # so we continue the cycle
        self.reset = False

        # We're a child shader so we inherit the parent (master shader) OpenGL context
        if gl_context is not None:
            self.gl_context = gl_context
        
        # Build coordinates based on self.flip
        self.__build_coordinates()

        # Info we send to the shaders read only (uniforms) that can and are generated on the main render loop
        self.pipeline = {
            # - mmv_time (float) -> time elapsed based on the frame rate of the shader in seconds
            "mmv_time": 0,
            
            # - mmv_frame (int) -> current frame number of the shader
            "mmv_frame": 0,
            
            # - mmv_resolution (vec2(int width, int height)) -> target output resolution
            "mmv_resolution": [0, 0],

            # - mmv_zoom (float) -> Scroll wheels zoom
            # - mmv_rotation (float) -> Target rotation in degrees
            "mmv_zoom": 1.0,
            "mmv_rotation": 0.0,

            # - mmv_drag (vec2(float)) -> Dragged pixels with mouse
            "mmv_drag": np.array([0.0, 0.0]),

            # Mouse position on screen, not normalized
            "mmv_mouse": [0, 0],

            # Are we flipped?
            "mmv_flip": -1 if self.flip else 1,
        }

        # If on real time view we want to freeze the shader for analysis
        self.freezed_pipeline = False

        # A dictionary that will hold indexes representing the location of textures
        # as well as the object we get it from:
        #
        # - Is it a static image? Do nothing just use its texture
        # - Is it a video? We need to get the next frame then upload to the GPU the texture
        # - Is it a shader? We need to render it
        # 
        # This dictionary is mostly for information on which loader we have and to organize its
        # object if we need to do some action.
        self.textures = {}

        # Dictionary to hold name: indexes on self.textures dictionary for writing to textures
        # used for communicating big data arrays between Python and the GPU
        # One example usage is for writing FFT values
        self.writable_textures = {}

        # Initialize None values
        (self.width, self.height, self.fps) = [None] * 3

        # # Refactors
        self.preprocessor = MMVShaderMGLPreprocessor(mmv_shader_mgl = self)
        self.window_handlers = MMVShaderMGLWindowHandlers(mmv_shader_mgl = self)

        # NOTE: Aliased functions on refactors, THIS MIGHT NOT APPEAR ON LINTING!!
        self.include_dir = self.preprocessor.include_dir
        self.mode = self.window_handlers.mode
        self.update_window = self.window_handlers.update_window

    # We might be asked to flip or not on a shader so we need to reconstruct those
    def __build_coordinates(self):

        # The buffer that represents the 4 points of the screen and their
        # respective uv coordinate. GL center is the coordinate (0, 0) and each
        # edge is either 1 or -1 relative to its axis. We keep that because central rotation
        
        # gl_bluv{x,y} -> "OpenGL" bottom left uv {x,y}
        gl_bluvx = -1.0  # Bottom Left X
        gl_bluvy = -1.0  # Bottom Left Y

        # gl_truv{x,y} -> "OpenGL" top right uv {x,y}
        gl_truvx =  1.0  # Top Right X
        gl_truvy =  1.0  # Top Right Y

        # What coordinate we swap the Y values to / for on Shadertoy and OpenGL coordinates?
        # ShaderToy flip we swap 1 to zero and opengl we swap -1 with 1 (multiply Y by 1 or -1)
        st_flip = [1, 0] if self.flip else [0, 1]
        gl_flip = -1 if self.flip else 1

        # Coordinates of the OpenGL Vertex positions on screen, the target UV for 
        # the OpenGL standard [(0, 0) center, edges are from -1 to 1] or Shadertoy ones
        # [(0, 0) bottom left, edges goes from 0 to 1]
        self.coordinates = [
            # OpenGL pos (X, Y)   OpenGL UV (U, V)                Shadertoy UV (U, V)
            gl_bluvx, gl_truvy,   gl_bluvx, gl_truvy * gl_flip,   0, st_flip[1],  # Top Left      [^ <]
            gl_bluvx, gl_bluvy,   gl_bluvx, gl_bluvy * gl_flip,   0, st_flip[0],  # Bottom Left   [v <]
            gl_truvx, gl_truvy,   gl_truvx, gl_truvy * gl_flip,   1, st_flip[1],  # Top Right     [^ >]
            gl_truvx, gl_bluvy,   gl_truvx, gl_bluvy * gl_flip,   1, st_flip[0],  # Bottom Right  [v >]
        ]

    # Create one FBO which is a texture under the hood so we can utilize it in some other shader
    # Returns [texture, fbo], which the texture is attached to the fbo with the previously
    # configured width, height
    def _construct_texture_fbo(self, verbose = True):
        debug_prefix = f"[MMVShaderMGL._construct_texture_fbo] [{self.name}]"

        # Error assertion, width height or fps is not set
        assert not any([value is None for value in [self.width, self.height]]), ("Width or height wasn't set / is None, did you call .render_config(width, height, fps) first?")
        if verbose: logging.info(f"{debug_prefix} Constructing an FBO attached to an Texture with [width={self.width}] [height=[{self.height}]")

        # Create a RGBA texture of this class's configured resolution, width and height can be supersampled AA
        texture = self.gl_context.texture((
            int(self.width * self.ssaa),
            int(self.height * self.ssaa)
        ), 4)

        # Create an FBO which is attached to that previous texture, whenever we render something
        # to this FBO after fbo.use()-ing it, the contents will be written directly on that texture
        # which we can bind to some location in other shader. This process is recursive

        # Create the FBO
        fbo = self.gl_context.framebuffer(color_attachments = [texture])

        # Return the two created objects
        return [texture, fbo]
    
    # Create FBO bound to a texture and render buffer
    def _create_assing_texture_fbo_render_buffer(self, verbose = True):
        if verbose: logging.info(f"[MMVShaderMGL._create_assing_texture_fbo_render_buffer] Creating and assigning RGBA Texture to some FBO and Render Buffer")
        self.texture, self.fbo = self._construct_texture_fbo(verbose = verbose)

    # Loads one shader from the disk, optionally also a custom vertex shader rather than the screen filling default one
    def load_shader_from_path(self, fragment_shader_path, vertex_shader_path = MMV_MGL_DEFAULT_VERTEX_SHADER):
        debug_prefix = f"[MMVShaderMGL.load_shader_from_path] [{self.name}]"
        self.fragment_shader_path = fragment_shader_path
        self.vertex_shader_path = vertex_shader_path

        # # Fragment shader

        #  Log action and error assertion, path must be valid
        logging.info(f"{debug_prefix} Loading fragment shader from path [{fragment_shader_path}]")
        assert (os.path.exists(fragment_shader_path)), f"Fragment shader path must be valid: [{fragment_shader_path}]"

        # Load the fragment shader file
        with open(fragment_shader_path, "r") as frag_shader:
            frag_data = frag_shader.read()

        # # Vertex shader
        
        # Vertex shader is optional so we load it later on if it was given a different input
        if vertex_shader_path != MMV_MGL_DEFAULT_VERTEX_SHADER:

            # Log action and error assertion, path must be valid
            logging.info(f"{debug_prefix} Loading fragment shader from path [{vertex_shader_path}]")
            assert (os.path.exists(vertex_shader_path)), f"Vertex shader path must be valid: [{vertex_shader_path}]"

            # Load the fragment shader file
            with open(vertex_shader_path, "r") as vertex_shader:
                vertex_data = vertex_shader.read()

        else: # Otherwise the vertex data is the default screen filling one
            vertex_data = MMV_MGL_DEFAULT_VERTEX_SHADER

        # # Construct the shader
        self.construct_shader(
            fragment_shader = frag_data,
            vertex_shader = vertex_data,
        )

    # Drop current stuff    , use some other fragment shader or vertex shader inserted from outside
    # (current self.fragment_shader and self.vertex_shader)
    def _read_shaders_from_paths_again(self):
        if self.master_shader:
            self.__reset_function()
            self.preprocessor.reset()

            # NOTE: Workaround on RAM leak, drop everything and treat as reload
            self.window_handlers.drop_textures()
            
            # Delete textures dictionray
            del self.textures
            self.textures = {}

            self.load_shader_from_path(
                fragment_shader_path = self.fragment_shader_path,
                vertex_shader_path = self.vertex_shader_path
            )

            # Just in case
            gc.collect()

    # Create one context's program out of a frag and vertex shader, those are used together
    # with VAOs so we render to some FBO. 
    # Parses for the preprocessor syntax for mappings
    # Also copies #pragma include <path.glsl> to this fragment shader
    def construct_shader(self,
        fragment_shader,
        vertex_shader = MMV_MGL_DEFAULT_VERTEX_SHADER,
        verbose = True,
    ):
        debug_prefix = f"[MMVShaderMGL.construct_shader] [{self.name}]"

        # The raw specification prefix, sets uniforms every one should have
        # we don't add just yet to the fragment shader because we can have some #pragma map
        # and we have to account for that before compiling the shader
        fragment_shader_prefix = MMV_MGL_FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX

        # # Join prefix and shader, replace values

        # Join the prefix and the fragment shader
        fragment_shader = f"{fragment_shader_prefix}\n{fragment_shader}"

        # Parse the shader with the preprocessor
        stuff = self.preprocessor.parse(shader = fragment_shader)
        fragment_shader = stuff["shader"]
        new_uniforms = stuff["new_uniforms"]

        # # Construct the shader

        # We might need our frag shader or vertex shader later on when we 
        # ._reconstruct_program() if the window gets rescaled
        self.fragment_shader = fragment_shader
        self.vertex_shader = vertex_shader

        # Create a program with the fragment and vertex shader
        self._create_program(
            fragment_shader = fragment_shader,
            vertex_shader = vertex_shader,
        )

        # Get a texture bound to the FBO
        if not self.master_shader:
            self._create_assing_texture_fbo_render_buffer(verbose = verbose)

        # Build the buffer we send when making the VAO
        self.fullscreen_buffer = self.gl_context.buffer(array('f', self.coordinates))
        self._create_vao()

        # Assign the uniforms to target values
        for name, value in new_uniforms:
            uniform = self.program.get(name, FakeUniform())
            uniform.value = value

    # Truly construct a shader, returns a ModernGL Program
    def _create_program(self, fragment_shader, vertex_shader):
        debug_prefix = f"[MMVShaderMGL._create_program] [{self.name}]"
        try:
            self.program = self.gl_context.program(fragment_shader = fragment_shader, vertex_shader = vertex_shader)
        except moderngl.error.Error as e:

            # Log faulty shader
            logging.error(f"{debug_prefix} Faulty GLSL:")
            for i, line in enumerate(fragment_shader.split("\n")):
                logging.error(f"[{i:04}] | {line}")
            logging.error(f"{debug_prefix} Error: {e}")

            # Drop textures since we'll not need them and return missing shader texture
            self.window_handlers.drop_textures()
            self.program = self.gl_context.program(
                fragment_shader = MMV_MGL_FALLBACK_MISSING_TEXTURE_SHADER,
                vertex_shader = MMV_MGL_DEFAULT_VERTEX_SHADER
            )

    # Create fullscreen VAO that reads position, OpenGL UV coordinates then ShaderToy UV coordinates
    def _create_vao(self):
        debug_prefix = f"[MMVShaderMGL._create_vao] [{self.name}]"
        logging.info(f"{debug_prefix} Creating VAO with Full Screen buffer")

        # Create one VAO on the program with the coordinate info
        self.vao = self.gl_context.vertex_array(
            self.program, [(
                # Fill the whole screen
                self.fullscreen_buffer,

                # Expect three pairs of floats and what they mean
                "2f 2f 2f",
                "in_pos", "in_opengl_uv", "in_shadertoy_uv"
            )],

            # Ignore unused vars, like, when we don't ever touch one uv coordinate system just 
            # keep going and don't blame the user we're not binding to an used attribute
            skip_errors = True
        )

    # # Loop functions, routines [usually recursive]

    # Write a certain data to a texture pipeline by its name on #pragma map-ed
    def write_texture_pipeline(self, texture_name, data, viewport = None):
        if not self.freezed_pipeline:

            # The index on the writable textures dictionary
            target_index = self.writable_textures.get(texture_name, None)

            # If it even does exist then we write to its respective texture
            # AttributeError will happen when / if we get a mgl.InvalidObject (dropped textures)
            if target_index is not None:
                try:
                    tex = self.textures[target_index]["texture"]
                    # d = data.copy()
                    # d.resize(tex.size)
                    tex.write(data, viewport = viewport)
                except KeyError: 
                    pass

            # Write recursively with same arguments
            for index in self.textures.keys():
                if self.textures[index]["loader"] == "shader":
                    self.textures[index]["shader_as_texture"].write_texture_pipeline(
                        texture_name = texture_name, data = data, viewport = viewport
                    )

    # Pipe a pipeline to a target that have a program attribute (this self class or shader as texture)
    def _pipe_pipeline(self, pipeline, target):
        debug_prefix = "[MMVShaderMGL._pipe_pipeline]"
            
        # Pass the pipeline values to the shader
        for key, value in pipeline.items():

            # If shader is frozen don't pipe any items unless it's core components like
            # zoom, drag, resolution
            letpass = [
                "drag", "zoom", "resolution", "rotation",
                "key", "debug"
            ]
            if (not self.freezed_pipeline) or (any( [item in key for item in letpass])):
                uniform = target.program.get(key, FakeUniform())
                if (not isinstance(value, float)) and (not isinstance(value, int)):
                    value = tuple(value)
                uniform.value = value

    # Render this shader to the FBO recursively, users are supposed to run .next()
    # with some custom pipeline, this just renders whatever info we have right now.
    def _render(self, pipeline):
        debug_prefix = "[MMVShaderMGL._render]"

        # Render every shader as texture recursively
        for index in self.textures.keys():
            if self.textures[index]["loader"] == "shader":

                # Send info about the pipeline
                self._pipe_pipeline(
                    pipeline = pipeline,
                    target = self.textures[index]["shader_as_texture"]
                )

                # Call this function again but for child shaders
                self.textures[index]["shader_as_texture"]._render(pipeline = pipeline)

        # Pipe the pipeline to self
        self._pipe_pipeline(pipeline = pipeline, target = self)

        # Render to the FBO using this VAO
        if self.master_shader:
            self.window_handlers.window.use()
            self.window_handlers.window.clear()
        else:
            self.fbo.use()
            self.fbo.clear()

        # The location is the dict index, the texture info is [name, loader, object]
        for location, texture_info in self.textures.items():

            # Unpack guaranteed generic items
            name = texture_info["name"]
            loader = texture_info["loader"]

            if loader == "shader":
                texture_obj = texture_info["shader_as_texture"].texture
            else:
                texture_obj = texture_info["texture"]

            try:  # TODO: Video that doesn't match target FPS should not read new frame for every frame
                # Read the next frame of the video
                if loader == "video":
                    import cv2

                    # We'll only have a fourth element that is video if loader is video
                    video = texture_info["capture"]
                    ok, frame = video.read()

                    # Can't read, probably out of frames?
                    if not ok:  # cry
                        # Reset to frame 0
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        # Read again
                        ok, frame = video.read()
                    
                    # No need to convert BGR -> RGB since video texture are already created with swizzle
                    texture_obj.write(frame)

                    if MMVShaderMGL.EXPERIMENTAL_VIDEO_MIPMAP:
                        texture_obj.build_mipmaps()

                # Set the location we'll expect this texture
                self.program[name] = location
                
                # Use it
                texture_obj.use(location = location)
            
            # Texture wasn't used, should error out on self.program[name]
            except KeyError:
                pass

        # Render to this class FBO
        self.vao.render(mode = moderngl.TRIANGLE_STRIP)
        
        if self.master_shader and (not self.window_handlers.headless) and (self.window_handlers.show_gui):
            self.window_handlers.render_ui()
            self.gl_context.enable_only(moderngl.NOTHING)

    # # User functions

    # Iterate through this class instance as a generator for getting the 
    def next(self, custom_pipeline = {}):

        # Interpolate zoom and drag
        self.pipeline["mmv_rotation"] = self.window_handlers.rotation
        self.pipeline["mmv_zoom"] = self.window_handlers.zoom
        self.pipeline["mmv_drag"] = self.window_handlers.drag

        # Set the pipeline attributes if shader is not frozen
        if not self.freezed_pipeline:
            self.pipeline["mmv_frame"] += 1
            self.pipeline["mmv_time"] = self.pipeline["mmv_frame"] / self.fps
        
        self.pipeline["is_dragging"] = self.window_handlers.is_dragging
        self.pipeline["is_gui_visible"] = self.window_handlers.show_gui
        self.pipeline["mmv_debug_mode"] = self.window_handlers.debug_mode

        # Keys
        self.pipeline["mmv_key_ctrl"] = self.window_handlers.ctrl_pressed
        self.pipeline["mmv_key_shift"] = self.window_handlers.shift_pressed
        self.pipeline["mmv_key_alt"] = self.window_handlers.alt_pressed

        if MMVShaderMGL.DEVELOPER_RAM_PROFILE:
            from mem_top import mem_top
            if self.pipeline["mmv_frame"] % 300 == 0:
                logging.debug(mem_top())

        # The resolution needs to be scaled with SSAA
        self.pipeline["mmv_resolution"] = (self.width * self.ssaa, self.height * self.ssaa)

        # Assign user custom pipelines.
        # NOTE: Don't forget to write (uniform (type) name;) on the GLSL file
        # and also be sure that the name is unique, we don't check this here due Python performance
        for key, value in custom_pipeline.items():
            self.pipeline[key] = value

        # print(self.pipeline)
        self._render(pipeline = self.pipeline)
            
    # Read from the current window FBO, return the bytes (remember that it can be headless window)
    def read(self): return self.window_handlers.window.fbo.read()
    
    # Write directly into a subprocess (FFmpeg, FFplay), use this for speeds preferably
    def read_into_subprocess_stdin(self, target_stdin):
        # target_stdin.write(self.window.fbo.read(viewport = self.window.viewport))
        target_stdin.write(self.window_handlers.window.fbo.read())

    # Return list of used variables in program
    def get_used_variables(self) -> list:
        if self.master_shader:

            # Create empty info            
            info = [k for k in self.program._members.keys()]

            # Call for every shader as texture loaders
            for index in self.textures.keys():
                if self.textures[index]["loader"] == "shader":
                    for key in self.textures[index]["shader_as_texture"].get_used_variables():
                        info.append(key)
            return info
        
        # Return child variables
        else: return [k for k in self.program._members.keys()]
