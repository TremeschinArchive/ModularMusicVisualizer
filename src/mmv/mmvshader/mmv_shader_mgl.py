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

from moderngl_window.integrations.imgui import ModernglWindowRenderer
from mmv.common.cmn_constants import STEP_SEPARATOR
from moderngl_window.conf import settings
from array import array
import moderngl_window
from PIL import Image
import subprocess
import moderngl
import logging
import shutil
import imgui
import time
import uuid
import cv2
import sys
import re
import os

# # # DOCUMENTATION

"""
# # # # # # Description

    This (big) file is intended to interface with moderngl Python package and provide
some bindings, utilities, a basic preprocessor, shortcuts for mapping images, videos,
pipelines, uniform values, deals with creating textures, window, contexts, rendering,
outputting etc. The main preprocessor is implemented here for those also.

    This also automatically includes some MMV specification at the start of the file
so some variable names are reserved or already defined. See below the prefixes

# # # # # # Usage

Within MMV the expected way is this:

| import mmv
| interface = mmv.MMVPackageInterface()
| shader_interface = interface.get_shader_interface()
| mgl = shader_interface.get_mgl_interface(master_shader = True)

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

- window_class: can be "glfw", "pyglet", "headless", etc, see moderngl_window docs.
- strict: Strict mode means to not by any means change the target width and height, render
    at fixed resolution
- vsync: Wait for buffer swap of the window
    NOTE: IMPORTANT: this heavily degrades MMV multithreaded code performance for some reason
        please write your own vsync if displaying real time.
    For render mode, vsync = False is preferred.
- msaa: Number of multi sampling anti aliasing to use. Shouldn't take much impact on
    performance since MMV doesn't yet works with many geometry

After that you're supposed to loader some master shader from path that renders the final
images only.

| mgl.load_shader_from_path(
|     fragment_shader_path,
|     replaces,
|     save_shaders_path
| )

TODO: NOTE: replaces dictionary replaces values matched in {NAME} on the file with the
    value's string. This will be moved to the ShaderMaker interface.

save_shaders_path saves the final preprocessed shaders so we can debug on what went wrong.
Send None for not saving those.

# # # # # # Preprocessor

This is the heart of why this file is so big. The general syntax is:
- #pragma function (options)

The easiest and simplest one is:
    - #pragma map name some_naming

    This internally sets the name of the file we save to the save_shaders_path for debugging

The next one is:
    - #pragma include name mode

    Name is the name (without the .glsl) of some file in the included directories.
    For example, if your directory have like:
    
    | include
    | | file1.glsl
    | | file2.glsl

    And you [#pragma include file1] it'll include the contents of the [file1.glsl]
    based on a mode.

    Mode can be one of the two:

    - multiple: Allow re-including, examples are:
        - [math_constants.glsl]
        - [coordinates_normalization.glsl]

    - once: Only ever include once this file in THIS loaded GLSL. Best example is
        includeing [mmv_specification.glsl] on the beginning of the file.

    This is for avoiding redefining values and functions, for that I advise also not
    to shadow variables, and use stuff like [math_constants.glsl] on the beginning of
    functions where you'll immediately use them.

The main (and most complex) mapping is this one:
    - #pragma map loader=name;value;[width]x[height]x[depth]

    We load some loader with the value interpreted accordingly.
    Width, height and depth not always will be used.

    For all loaders it'll add these variables on the code:
        - sampler2D with name [name], the texture to read from
        - vec2 with name [name]_resolution storing the width and height
        - int with name [name]_width storing the width
        - int with name [name]_height storing the height

    Here's the info on each loader:

    - loader=image: (see *1. below)
        This loads some raw contents of a image on the system given by its path
        stored on the [value]

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
        I called this "dynamic shader", it does not require width and height and its 
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
DEFAULT_VERTEX_SHADER = """\
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
FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX = """\
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

// Audio values
uniform float smooth_audio_amplitude;
uniform float smooth_audio_amplitude2;
uniform float progressive_amplitude;
uniform vec3 standard_deviations;
uniform vec3 mmv_rms_lrm;

///add_uniform"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Transparent, black shader, used for ignoring a certain layer quickly
# Usage:
# | #pragma map some_other_unwanted_shader=dynshader;MMVMGL_NULL_SHADER
# | ... GLSL code
MMVMGL_NULL_SHADER = "void main() { fragColor = vec4(0.0); }"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# When an uniform is not used it doesn't get initialized on the program
# so we .get(name, FakeUniform()) so we don't get errors here
class FakeUniform:
    value = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MMVShaderMGL:

    # # Window management, contexts

    # Configurate how we'll output the shader
    def target_render_settings(self, width, height, fps, ssaa = 1, silent = False):
        debug_prefix = "[MMVShaderMGL.target_render_settings]"
        (self.width, self.height, self.fps, self.ssaa) = (width, height, fps, ssaa)
        if not silent:
            logging.info(f"{debug_prefix} Render configuration is [width={self.width}] [height=[{self.height}] [fps=[{self.fps}] [ssaa={self.ssaa}]")
    
    # Which "mode" to render, window loader class, msaa, ssaa, vsync, force res?
    def mode(self, window_class, msaa = 1, vsync = True, strict = False, icon = None):
        debug_prefix = "[MMVShaderMGL.mode]"

        # Get function arguments
        self.headless = window_class == "headless"
        self.strict = strict
        self.vsync = vsync
        self.msaa = msaa

        # Headless we disable vsync because we're rendering only..?
        # And also force aspect ratio just in case (strict option)
        if self.headless:
            self.strict = True
            self.vsync = False

        # Assign the function arguments
        settings.WINDOW["class"] = f"moderngl_window.context.{window_class}.Window"
        settings.WINDOW["aspect_ratio"] = self.width / self.height
        settings.WINDOW["vsync"] = self.vsync
        settings.WINDOW["title"] = "MMVShaderMGL Window"
        settings.WINDOW["size"] = (self.width, self.height)

        # Create the window
        self.window = moderngl_window.create_window_from_settings()

        # Make sure we render strictly into the resolution we asked
        if strict:
            # self.window.set_default_viewport()
            self.window.fbo.viewport = (0, 0, self.width, self.height)

        # Set the icon
        if icon is not None:
            self.window.set_icon(icon_path = icon)
        
        # The context we'll use is the one from the window
        self.gl_context = self.window.ctx
        self.window_should_close = False

        # Functions of the window if not headless
        if not self.headless:
            self.window.resize_func = self.window_resize
            self.window.key_event_func = self.key_event
            self.window.mouse_position_event_func = self.mouse_position_event
            self.window.mouse_drag_event_func = self.mouse_drag_event
            self.window.mouse_scroll_event_func = self.mouse_scroll_event
            self.window.mouse_press_event_func = self.mouse_press_event
            self.window.mouse_release_event_func = self.mouse_release_event
            self.window.unicode_char_entered_func = self.unicode_char_entered
            self.window.close_func = self.close
            imgui.create_context()
            self.imgui = ModernglWindowRenderer(self.window)

    # [NOT HEADLESS] Window was resized, update the width and height so we render with the new config
    def window_resize(self, width, height):
        if hasattr(self, "strict"):
            if self.strict:
                return

        # Set width and height
        self.width = int(width)
        self.height = int(height)

        # Recursively call this function on every shader on textures dicionary
        for index in self.textures.keys():
            if self.textures[index]["loader"] == "shader":
                self.textures[index]["shader_as_texture"].window_resize(
                    width = self.width, height = self.height
                )

        # Search for dynamic shaders and update them
        for index in self.textures.keys():
            if self.textures[index].get("dynamic", False):
                # Release OpenGL stuff
                self.textures[index]["shader_as_texture"].render_buffer.release()
                self.textures[index]["shader_as_texture"].texture.release()
                self.textures[index]["shader_as_texture"].fbo.release()
                self.textures[index]["shader_as_texture"].vao.release()

                # Create new ones in place
                self.textures[index]["shader_as_texture"].create_vao()
                self.textures[index]["shader_as_texture"].create_assing_texture_fbo_render_buffer(silent = True)

                # Assign texture
                self.textures[index]["texture"] = self.textures[index]["shader_as_texture"].texture

        # Master shader has window and imgui
        if self.master_shader:
            if not self.headless:
                self.imgui.resize(self.width, self.height)

            # Window viewport
            self.window.fbo.viewport = (0, 0, self.width, self.height)

    # Close the window
    def close(self, *args, **kwargs):
        self.window_should_close = True

    # Swap the window buffers, be careful if vsync is False and you have a heavy
    # shader, it will consume all of your GPU computation and will most likely freeze
    # the video
    def update_window(self):
        self.window.swap_buffers()

    # # Imgui functions

    def key_event(self, key, action, modifiers):
        self.imgui.key_event(key, action, modifiers)
    def mouse_position_event(self, x, y, dx, dy):
        self.imgui.mouse_position_event(x, y, dx, dy)
    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)
    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)
    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)
    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)
    
    # Render the user interface
    def render_ui(self):

        # Test window
        imgui.new_frame()
        imgui.begin("Custom window", True)
        imgui.text("Bar")
        imgui.text_colored("Eggs", 0.2, 1., 0.)
        imgui.end()

        # Render
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    # # Generic methods

    def __init__(self, flip = False, master_shader = False, gl_context = None):
        debug_prefix = "[MMVShaderMGL.__init__]"
        self.master_shader = master_shader
        self.flip = flip
        self.ssaa = 1

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
        }

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

        # When we use [#pragma include name/path] we have the option to put a directory or a name in there, 
        # we search for these paths for a file that is named [name.glsl] so we don't have to pass the full
        # path and make this act kinda like a (lazy | compact) method of including other shaders.
        #
        # The included files dir is for files we already included so we don't include twice and cause
        # redefinition errors
        self.include_directories = []
        self.included_files = []

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

    # Add a directory to the list of directories to include, note that this will recursively add this
    # include dir to the shaders as textures mapped
    def include_dir(self, path):
        debug_prefix = "[MMVShaderMGL.include_dir]"
        
        # Log action
        logging.info(f"{debug_prefix} Add path to include directories [{path}]")

        # If the path was already included then don't do anything
        if path in self.include_directories:
            logging.info(f"{debug_prefix} Path was already included in the include directories")
        else:
            self.include_directories.append(path)

        # Recursively adding this path to child shaders
        logging.info(f"{debug_prefix} Path was already included in the include directories")

        # Add recursively the paths as well
        for index in self.textures:
            if self.texture[index]["loader"] == "shader":
                self.textures[index]["shader_as_texture"].include_dir(path = path)

    # Create one FBO which is a texture under the hood so we can utilize it in some other shader
    # Returns [texture, fbo], which the texture is attached to the fbo with the previously
    # configured width, height
    def construct_texture_fbo(self, silent = False):
        debug_prefix = "[MMVShaderMGL.construct_texture_fbo]"

        # Error assertion, width height or fps is not set
        assert not any([value is None for value in [self.width, self.height]]), (
            "Width or height wasn't set / is None, did you call .render_config(width, height, fps) first?"
        )
        
        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Constructing an FBO attached to an Texture with [width={self.width}] [height=[{self.height}]")

        # Create a RGBA texture of this class's configured resolution, width and height can be supersampled AA
        texture = self.gl_context.texture((
            int(self.width * self.ssaa),
            int(self.height * self.ssaa)
        ), 4)

        # Create an FBO which is attached to that previous texture, whenever we render something
        # to this FBO after fbo.use()-ing it, the contents will be written directly on that texture
        # which we can bind to some location in other shader. This process is recursive

        # Create the Render Buffer
        render_buffer = self.gl_context.renderbuffer((
            int(self.width * self.ssaa), int(self.height * self.ssaa)
        ))

        # Create the FBO
        fbo = self.gl_context.framebuffer(color_attachments = [texture, render_buffer])

        # Return the two created objects
        return [texture, fbo, render_buffer]
    
    # Loads one shader from the disk, optionally also a custom vertex shader rather than the screen filling default one
    def load_shader_from_path(self, fragment_shader_path, replaces = {}, vertex_shader_path = DEFAULT_VERTEX_SHADER, save_shaders_path = None):
        debug_prefix = "[MMVShaderMGL.load_shader_from_path]"

        # # Fragment shader

        #  Log action and error assertion, path must be valid
        logging.info(f"{debug_prefix} Loading fragment shader from path [{fragment_shader_path}]")
        assert (os.path.exists(fragment_shader_path)), f"Fragment shader path must be valid: [{fragment_shader_path}]"

        # Load the fragment shader file
        with open(fragment_shader_path, "r") as frag_shader:
            frag_data = frag_shader.read()

        # # Vertex shader
        
        # Vertex shader is optional so we load it later on if it was given a different input
        if vertex_shader_path != DEFAULT_VERTEX_SHADER:

            # Log action and error assertion, path must be valid
            logging.info(f"{debug_prefix} Loading fragment shader from path [{vertex_shader_path}]")
            assert (os.path.exists(vertex_shader_path)), f"Vertex shader path must be valid: [{vertex_shader_path}]"

            # Load the fragment shader file
            with open(vertex_shader_path, "r") as vertex_shader:
                vertex_data = vertex_shader.read()

        else: # Otherwise the vertex data is the default screen filling one
            vertex_data = DEFAULT_VERTEX_SHADER
        
        # # Construct the shader
        
        self.construct_shader(
            fragment_shader = frag_data,
            replaces = replaces,
            vertex_shader = vertex_data,
            save_shaders_path = save_shaders_path,
        )

    # Create one context's program out of a frag and vertex shader, those are used together
    # with VAOs so we render to some FBO. 
    # Parses for #pragma map name=loader:value:WxH and creates the corresponding texture, binds to it
    # Also copies #pragma include <path.glsl> to this fragment shader
    def construct_shader(self,
        fragment_shader, replaces = {},
        vertex_shader = DEFAULT_VERTEX_SHADER,
        save_shaders_path: str = None,  # Path we save the final fragment and vertex shader based on its name
    ):
        debug_prefix = "[MMVShaderMGL.construct_shader]"

        # The raw specification prefix, sets uniforms every one should have
        # we don't add just yet to the fragment shader because we can have some #pragma map
        # and we have to account for that before compiling the shader
        fragment_shader_prefix = FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX

        # # Join prefix and shader, replace values

        # Join the prefix and the fragment shader
        fragment_shader = f"{fragment_shader_prefix}\n{fragment_shader}"

        # Iterate on items
        for key, value in replaces.items():

            # We surround the one we replace with {} for visibility on the GLSL
            key = "{" + str(key) + "}"
            
            # How many is there to replace?
            found = fragment_shader.count(key)
            logging.info(f"{debug_prefix} Replacing [N={found}] on shader [{key}] -> [{value}]")

            # Actually replace
            fragment_shader = fragment_shader.replace(key, str(value))

        # # Parse the shader

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma map")

        # # Name

        self.name = str(uuid.uuid4())
        regex = r"([ ]+)?#pragma map name ([\w]+)"
        found = re.findall(regex, fragment_shader, re.MULTILINE)

        # Try find the name of the shader
        for mapping in found:
            identation, name = mapping
            self.name = name

        # # Do flip?

        logging.info(f"{debug_prefix} Parsing the fragment shader for any #pragma flip [true, false]")

        regex = r"^#pragma flip ([\w]+)"
        found = re.findall(regex, fragment_shader, re.MULTILINE)

        for occurence in found:
            self.flip = True if (occurence == "true") else False
            self.__build_coordinates()

        # # Loaders

        # Regular expression to match #pragma map name=loader:/path/value;512x512
        # the ;512x512 is required for the image, video and shader loaders
        regex = r"([ ]+)?#pragma map ([\w]+)=([\w]+);([\w/\\:. -]+)?;?([0-9]+)?x?([0-9]+)?x?([0-9]+)?"
        found = re.findall(regex, fragment_shader, re.MULTILINE)
    
        logging.info(f"{debug_prefix} Regex findall says: {found}")

        # The static uniforms we'll assign the values to (eg. image, video, shader resolutions)
        assign_static_uniforms = []

        # For each mapping
        for mapping in found:

            # Get the values we matched. Not all loaders accept width, height or depth
            # See documentation at the top
            identation, name, loader, value, width, height, depth = mapping
            logging.info(f"{debug_prefix} Matched mapping [name={name}] [loader={loader}] [value={value}] [width={width}] [height={height}] [depth={depth}]")

            # Remove the original #pragma map, seems like NVIDIA cards specific problem
            full_pragma_map = f"\n{identation}#pragma map {name}={loader};{value}"
            
            # Optional ones
            if (width != "") and (height != ""):
                full_pragma_map += f";{width}x{height}"
            if (depth != ""):
                full_pragma_map += f";{depth}"

            # Remove pragma map
            logging.info(f"{debug_prefix} Removing original [{full_pragma_map}]")
            fragment_shader = fragment_shader.replace(full_pragma_map,
                f"// was pragma map [name={name}] [loader={loader}] [value={value}] [width={width}] [height=[{height}] [depth={depth}]"
            )

            # Error assertion, valid loader and path
            loaders = ["image", "video", "shader", "dynshader", "pipeline_texture", "include"]
            assert loader in loaders, f"Loader not implemented in loaders {loaders} for [{full_pragma_map}] [{mapping}]"

            # All but pipeline texture must be valid paths
            if (not loader in ["pipeline_texture"]) and (value != "MMVMGL_NULL_SHADER"):
                assert os.path.exists(value), f"Value of loader [{value}] is not a valid path in [{full_pragma_map}] [{mapping}]"

            # We'll map one texture to this shader, either a static image, another shader or a video
            # we do create and store the shader and video objects so we render or get the next image later on before using
            if loader in ["image", "shader", "dynshader", "video", "pipeline_texture"]:

                # We need an target render size if it's all but dynshader
                if loader != "dynshader":
                    assert (width != '') and (height != ''), "Width or height shouldn't be null, set WxH on pragma map with :512x512"

                    # Convert to int the width and height
                    width, height = int(width), int(height)
                else:
                    width = self.width
                    height = self.height

                # Image loader, load image, convert to RGBA, create texture with target resolution, assign texture
                if loader == "image":

                    # Load the image, get width and height for the texture size
                    img = Image.open(value).convert("RGBA")
                    width, height = img.size

                    # Convert image to bytes and upload the texture to the GPU
                    logging.info(f"{debug_prefix} Uploading texture to the GPU")
                    texture = self.gl_context.texture((width, height), 4, img.tobytes())

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[len(self.textures.keys()) + 1] = {
                        "name": name,
                        "loader": "texture",
                        "texture": texture
                    }
                
                # We create a black texture that some other pipeline is supposed to write on, this is mostly used
                # when we need to communicate big arrays that we keep changing. Totally destroys performance if
                # you keep writing into a big texture
                elif loader == "pipeline_texture":
                    logging.info(f"{debug_prefix} Creating black pipeline texture object")
                    
                    # Create a blank texture..
                    texture = self.gl_context.texture((width, height), int(depth), dtype = "f4")

                    # Assign the name, type and texture to the textures dictionary
                    assign_index = len(self.textures.keys())
                    
                    self.textures[assign_index] = {
                        "name": name, 
                        "loader": "texture",
                        "texture": texture
                    }

                    # Put into the writable textures dictionary
                    self.writable_textures[name] = assign_index
                
                # Add shader as texture element
                # shader is strict resolution
                # dynshader adapts to the viewport
                elif (loader == "shader") or (loader == "dynshader"):

                    # Null shader
                    if value == "MMVMGL_NULL_SHADER":
                        logging.info(f"{debug_prefix} Shader loader is MMVMGL_NULL_SHADER")
                        loader_frag_shader = MMVMGL_NULL_SHADER
                    
                    else:
                        # Read the shader we'll map
                        with open(value, "r") as f:
                            loader_frag_shader = f.read()

                    # Create one instance of this very own class
                    if self.master_shader:
                        f = not self.flip
                    else:
                        f = not self.flip

                    # Construct a class of this same type of the master shader, use the same context
                    shader_as_texture = MMVShaderMGL(flip = f, gl_context = self.gl_context)

                    # Add included dirs
                    for directory in self.include_directories:
                        shader_as_texture.include_dir(directory)

                    # Set the render configuration on the #pragma map for width, height. We don't need fps
                    # as that one will receive the main class's pipeline
                    shader_as_texture.target_render_settings(width = int(width), height = int(height), ssaa = self.ssaa, fps = None)

                    # Create a texture and fbo for this mapped shader, here is where we render to the fbo
                    # which is attached to the texture, and we use that texture in this main class
                    texture, fbo, _ = shader_as_texture.construct_texture_fbo()

                    # Construct the shader we loaded
                    shader_as_texture.construct_shader(
                        fragment_shader = loader_frag_shader, replaces = replaces,
                        save_shaders_path = save_shaders_path
                    )

                    # Next available id
                    assign_index = len(self.textures.keys())

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[assign_index] = {
                        "shader_as_texture": shader_as_texture,
                        "texture": shader_as_texture.texture,
                        "dynamic": loader == "dynshader",
                        "loader": "shader",
                        "name": name,
                    }

                # Video loader
                elif loader == "video":

                    # Get one VideoCapture
                    video = cv2.VideoCapture(value)

                    # Create a RGB texture for the video
                    texture = self.gl_context.texture((width, height), 3)
                    texture.swizzle = 'BGR'

                    # Next available id
                    assign_index = len(self.textures.keys())

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[assign_index] = {
                        "name": name,
                        "loader": "video",
                        "texture": texture,
                        "capture": video,
                    }
                    
                # Add the texture uniform values
                marker = "///add_uniform"
                fragment_shader = fragment_shader.replace(f"{marker}", f"\n// Texture\n{marker}")
                fragment_shader = fragment_shader.replace(f"{marker}", f"uniform sampler2D {name};\n{marker}")
                fragment_shader = fragment_shader.replace(f"{marker}", f"uniform int {name}_width;\n{marker}")
                fragment_shader = fragment_shader.replace(f"{marker}", f"uniform int {name}_height;\n{marker}\n")
                fragment_shader = fragment_shader.replace(f"{marker}", f"uniform vec2 {name}_resolution;\n{marker}\n")
    
                # The attributes we'll put into the previous values
                assign_static_uniforms += [
                    [f"{name}_width", int(width)],
                    [f"{name}_height", int(height)],
                    [f"{name}_resolution", (int(width), int(height))],
                ]

        # # Get #pragma includes

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma include")
        
        # Simple regex and get every match with findall
        regex = r"([ ]+)?#pragma include ([\w/. -]+) ([\w]+)?"
        found = re.findall(regex, fragment_shader, re.MULTILINE)

        logging.info(f"{debug_prefix} Regex findall says: {found}")
 
        # For each #pragma include we found
        for mapping in found:
            identation, include, mode = mapping

            # If this include was already made then no need to do it again.
            # mode "multiple" bypasses this
            if mode == "once":
                if include in self.included_files:
                    logging.info(f"{debug_prefix} File / path already included [{include}]")
                    continue
            
            # Mark that this was already included
            self.included_files.append(include)

            # This will replace this line (we build back)
            replaces = f"{identation}#pragma include {include} {mode}"

            # # Attempt to find the file on the included directories

            look_for_in_included_directories = f"{include}.glsl"
            logging.info(f"{debug_prefix} Checking on include directories [{self.include_directories}] for [{look_for_in_included_directories}]")
            include_found = False

            # Check for the include dirs files with the include value dot glsl
            # break the loops if we ever get a match
            for directory in self.include_directories:
                if include_found: break
                # For each file
                for file in os.listdir(directory):
                    if include_found: break

                    # If the file name takes the included name and ends with .glsl
                    if file == look_for_in_included_directories:
                        include_found = True

                        # The full path of the included shader path
                        include_shader_path = os.path.join(directory, file)                        
                        logging.info(f"{debug_prefix} Found a match at [{include_shader_path}]")

                        # Open the file
                        with open(include_shader_path, "r") as glsl:

                            # Add the identation of the match
                            include_other_glsl_data = []
                            for line in glsl:
                                include_other_glsl_data.append(f"{identation}{line}")

                            # Join the value this #pragma include replaces with the idented data of the other glsl
                            include_other_glsl_data = ''.join(include_other_glsl_data)
                            fragment_shader = fragment_shader.replace(replaces, include_other_glsl_data, 1)  # Replace ONCE

            # Continue to the next mapping, don't break this outer for loop but call it done here
            # since one file on the include directories was found
            if include_found: continue

            # # No file found on include directories, assuming user sent a path

            # Error assertion, the path must exist
            assert os.path.exists(include), f"Value of #pragma include is not a valid path [{include}]"

            # Read the other shader data
            with open(include, "r") as f:
                include_other_glsl_data = f.read()

            # Replace the line on this fragment shader with the included other one
            fragment_shader = fragment_shader.replace(replaces, include_other_glsl_data, 1)  # Replace ONCE

        # Pretty print / log
        if False:
            s = "-" * shutil.get_terminal_size()[0]
            frag_shader_prettyprint = '\n'.join([f"[{str(lineno).ljust(5)}] | {line}" for lineno, line in enumerate(fragment_shader.split("\n"))])
            vert_shader_prettyprint = '\n'.join([f"[{str(lineno).ljust(5)}] | {line}" for lineno, line in enumerate(vertex_shader.split("\n"))])
            print(s)
            logging.info(f"{debug_prefix} Fragment shader is:\n{frag_shader_prettyprint}")
            print(s)
            logging.info(f"{debug_prefix} Vertex shader is:\n{vert_shader_prettyprint}")
            print(s)

        # Do save the shaders to some path?
        if save_shaders_path is not None:
            base = f"{save_shaders_path}{os.path.sep}{self.name}"
            with open(f"{base}-frag.glsl", "w") as f:
                f.write(fragment_shader)

        # # Construct the shader

        # We might need our frag shader or vertex shader later on when we 
        # .__reconstruct_program() if the window gets rescaled
        self.fragment_shader = fragment_shader
        self.vertex_shader = vertex_shader

        # Create a program with the fragment and vertex shader
        self.program = self.create_program(
            fragment_shader = fragment_shader,
            vertex_shader = vertex_shader,
        )

        # Get a texture bound to the FBO
        if not self.master_shader:
            self.create_assing_texture_fbo_render_buffer()

        # Build the buffer we send when making the VAO
        self.fullscreen_buffer = self.gl_context.buffer(array('f', self.coordinates))
        self.create_vao()

        # Assign the uniforms to blank value
        for name, value in assign_static_uniforms:
            uniform = self.program.get(name, FakeUniform())
            uniform.value = value

    # Truly construct a shader
    def create_program(self, fragment_shader, vertex_shader):
        return self.gl_context.program(fragment_shader = fragment_shader, vertex_shader = vertex_shader)

    # Create FBO binded to a texture and render buffer
    def create_assing_texture_fbo_render_buffer(self, silent = False):
        self.texture, self.fbo, self.render_buffer = self.construct_texture_fbo(silent = silent)

    # Create fullscreen VAO
    def create_vao(self):
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

    # Drop current program, use some other fragment shader or vertex shader inserted from outside
    # (current self.fragment_shader and self.vertex_shader)
    def __reconstruct_program(self):
        self.program.release()
        self.program = self.create_program(
            self.fragment_shader, self.vertex_shader
        )

    # # Loop functions, routines

    # Write a certain data to a texture pipeline by its name on #pragma map-ed
    def write_texture_pipeline(self, texture_name, data):
        
        # The index on the writable textures dictionary
        target_index = self.writable_textures.get(texture_name, None)

        # If it even does exist then we write to its respective texture
        if target_index is not None:
            self.textures[target_index]["texture"].write(data)

        # Write recursively with same arguments
        for index in self.textures.keys():
            if self.textures[index]["loader"] == "shader":
                self.textures[index]["shader_as_texture"].write_texture_pipeline(texture_name = texture_name, data = data)

    # Pipe a pipeline to a target that have a program attribute (this self class or shader as texture)
    def pipe_pipeline(self, pipeline, target):
        debug_prefix = "[MMVShaderMGL.pipe_pipeline]"

        # Pass the pipeline values to the shader
        for key, value in pipeline.items():
            uniform = target.program.get(key, FakeUniform())
            uniform.value = value
    
    # Render this shader to the FBO recursively
    def render(self, pipeline):
        debug_prefix = "[MMVShaderMGL.render]"

        # Render every shader as texture recursively
        for index in self.textures.keys():
            if self.textures[index]["loader"] == "shader":
                self.pipe_pipeline(
                    pipeline = pipeline,
                    target = self.textures[index]["shader_as_texture"]
                )
                self.textures[index]["shader_as_texture"].render(pipeline = pipeline)

        # Pipe the pipeline to self
        self.pipe_pipeline(pipeline = pipeline, target = self)

        # Render to the FBO using this VAO
        if self.master_shader:
            self.window.use()
            self.window.clear()
        else:
            self.fbo.use()
            self.fbo.clear()

        # The location is the dict index, the texture info is [name, loader, object]
        for location, texture_info in self.textures.items():

            # Unpack guaranteed generic items
            name = texture_info["name"]
            loader = texture_info["loader"]
            texture_obj = texture_info["texture"]

            try:
                # Read the next frame of the video
                if loader == "video":

                    # We'll only have a fourth element that is video if loader is video
                    video = texture_info["capture"]
                    ok, frame = video.read()

                    # Can't read, probably out of frames?
                    if not ok:  # cry
                        # Reset to frame 0
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        # Read again
                        ok, frame = video.read()
                    
                    # Flip the image TODO: flip in GLSL by inverting uv? Also interpret BGR as RGB?
                    # frame = cv2.flip(frame, 0)
                    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    texture_obj.write(frame)

                # Set the location we'll expect this texture
                self.program[name] = location
                
                # Use it
                texture_obj.use(location = location)
            
            # Texture wasn't used, should error out on self.program[name]
            except KeyError:
                pass

        # Render to this class FBO
        self.vao.render(mode = moderngl.TRIANGLE_STRIP)
        
        # if not self.headless:
            # self.render_ui()

    # Iterate through this class instance as a generator for getting the 
    def next(self, custom_pipeline = {}):

        # Set the pipeline attributes
        self.pipeline["mmv_frame"] += 1
        self.pipeline["mmv_time"] = round((self.pipeline["mmv_frame"] / self.fps), 3)
        self.pipeline["mmv_resolution"] = (self.width * self.ssaa, self.height * self.ssaa)

        # Assign user custom pipelines.
        # NOTE: Don't forget to write (uniform (type) name;) on the GLSL file
        # and also be sure that the name is unique, we don't check this here due Python performance
        for key, value in custom_pipeline.items():
            self.pipeline[key] = value

        # print(self.pipeline)
        self.render(pipeline = self.pipeline)
            
    # Read from the current FBO, return the bytes
    def read(self):
        return self.window.fbo.read()
    
    # Write directly into a subprocess (FFmpeg, FFplay)
    # Use this for speeds preferably
    def read_into_subprocess_stdin(self, target_stdin):
        # target_stdin.write(self.window.fbo.read(viewport = self.window.viewport))
        target_stdin.write(self.window.fbo.read())
