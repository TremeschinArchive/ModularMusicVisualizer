"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Render shaders to video files or preview them realtime, map images,
videos and even other shaders as textures into a main one

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

from mmv.common.cmn_constants import STEP_SEPARATOR
from array import array
from PIL import Image
import subprocess
import moderngl
import logging
import shutil
import time
import cv2
import sys
import re
import os

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

///add_uniform"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# When an uniform is not used it doesn't get initialized on the program
# so we .get(name, FakeUniform()) so we don't get errors here
class FakeUniform:
    value = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MMVShaderMGL:

    # Create a headless OpenGL context  TODO: support for window mode (performance)?
    gl_context = moderngl.create_context(standalone = True)

    def __init__(self, flip = True):
        debug_prefix = "[MMVShaderMGL.__init__]"
        self.flip = flip

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
        st_flip = [1, 0] if self.flip else [0, 1]
        gl_flip = -1 if self.flip else 1

        # Coordinates of the OpenGL Vertex positions on screen, the target UV for 
        # the OpenGL standard [(0, 0) center, edges are from -1 to 1] or Shadertoy ones
        # [(0, 0) bottom left, edges goes from 0 to 1]
        coordinates = [
            # OpenGL pos (X, Y)   OpenGL UV (U, V)                Shadertoy UV (U, V)
            gl_bluvx, gl_truvy,   gl_bluvx, gl_truvy * gl_flip,   0, st_flip[1],  # Top Left      [^ <]
            gl_bluvx, gl_bluvy,   gl_bluvx, gl_bluvy * gl_flip,   0, st_flip[0],  # Bottom Left   [v <]
            gl_truvx, gl_truvy,   gl_truvx, gl_truvy * gl_flip,   1, st_flip[1],  # Top Right     [^ >]
            gl_truvx, gl_bluvy,   gl_truvx, gl_bluvy * gl_flip,   1, st_flip[0],  # Bottom Right  [v >]
        ]

        # Build the buffer we send when making the VAO
        self.fullscreen_buffer = MMVShaderMGL.gl_context.buffer(array('f', coordinates))

        # Info we send to the shaders read only (uniforms)
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

        # This next list holds instances of this very own class, MMVShaderMGL,
        # they are shaders the user mapped and we render them separately to a FBO
        # so we can use that as a texture <here> on this main class's shader
        self.shaders_as_textures = []

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
        for shader_as_texture in self.shaders_as_textures:
            shader_as_texture.add_include_dir(path = path)

    # Configurate how we'll output the shader
    def render_config(self, width, height, fps):
        debug_prefix = "[MMVShaderMGL.config]"
        (self.width, self.height, self.fps) = (width, height, fps)
        
    # Create one FBO which is a texture under the hood so we can utilize it in some other shader
    # Returns [texture, fbo], which the texture is attached to the fbo with the previously
    # configured width, height
    def construct_texture_fbo(self):
        debug_prefix = "[MMVShaderMGL.construct_texture_fbo]"

        # Error assertion, width height or fps is not set
        assert not any([value is None for value in [self.width, self.height]]), (
            "Width or height wasn't set / is None, did you call .render_config(width, height, fps) first?"
        )
        
        # Log action
        logging.info(f"{debug_prefix} Constructing an FBO attached to an Texture with [width={self.width}] [height=[{self.height}]")

        # Create a RGBA texture of this class's configured resolution
        texture = MMVShaderMGL.gl_context.texture((self.width, self.height), 4)

        # Create an FBO which is attached to that previous texture, whenever we render something
        # to this FBO after fbo.use()-ing it, the contents will be written directly on that texture
        # which we can bind to some location in other shader. This process is recursive
        fbo = MMVShaderMGL.gl_context.framebuffer(color_attachments = [texture])

        # Return the two created objects
        return [texture, fbo]
    
    # Loads one shader from the disk, optionally also a custom vertex shader rather than the screen filling default one
    def load_shader_from_path(self, fragment_shader_path, vertex_shader_path = DEFAULT_VERTEX_SHADER):
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
            vertex_shader = vertex_data,
        )

    # Create one context's program out of a frag and vertex shader, those are used together
    # with VAOs so we render to some FBO. 
    # Parses for #pragma map name=loader:value:WxH and creates the corresponding texture, binds to it
    # Also copies #pragma include <path.glsl> to this fragment shader
    def construct_shader(self, fragment_shader, vertex_shader = DEFAULT_VERTEX_SHADER):
        debug_prefix = "[MMVShaderMGL.construct_shader]"

        # The raw specification prefix, sets uniforms every one should have
        # we don't add just yet to the fragment shader because we can have some #pragma map
        # and we have to account for that before compiling the shader
        fragment_shader_prefix = FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX

        # # Parse the shader

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma map")

        # Regular expression to match #pragma map name=loader:/path/value;512x512
        # the ;512x512 is required for the image, video and shader loaders
        regex = r"([ ]+)?#pragma map ([\w]+)=([\w]+):([\w/. -]+):?([0-9]+)?x?([0-9]+)?"
        found = re.findall(regex, fragment_shader, re.MULTILINE)

        logging.info(f"{debug_prefix} Regex findall says: {found}")

        # The static uniforms we'll assign the values to (eg. image, video, shader resolutions)
        assign_static_uniforms = []

        # For each mapping
        for mapping in found:

            # Get the values we matched
            identation, name, loader, value, width, height = mapping
            logging.info(f"{debug_prefix} Matched mapping [name={name}] [loader={loader}] [width={width}] [height={height}]")

            # Error assertion, valid loader and path
            loaders = ["image", "video", "shader", "include"]
            assert loader in loaders, f"Loader not implemented in loaders {loaders}"
            assert os.path.exists(value), f"Value of loader [{value}] is not a valid path"

            # We'll map one texture to this shader, either a static image, another shader or a video
            # we do create and store the shader and video objects so we render or get the next image later on before using
            if loader in ["image", "shader", "video"]:

                # We need an target render size
                assert (width != '') and (height != ''), "Width or height shouldn't be null, set WxH on pragma map with :512x512"

                # Convert to int the width and height
                width, height = int(width), int(height)

                # Image loader
                if loader == "image":
                    # Load the image, get width and height for the texture size
                    img = Image.open(value).convert("RGBA")
                    width, height = img.size

                    # Convert image to bytes and upload the texture to the GPU
                    logging.info(f"{debug_prefix} Uploading texture to the GPU")
                    texture = MMVShaderMGL.gl_context.texture((width, height), 4, img.tobytes())

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[len(self.textures.keys()) + 1] = [name, "texture", texture]
                    
                # Add shader as texture element
                elif loader == "shader":

                    # Read the shader we'll map
                    with open(value, "r") as f:
                        loader_frag_shader = f.read()

                    # Create one instance of this very own class
                    shader_as_texture = MMVShaderMGL(flip = not self.flip)

                    # Set the render configuration on the #pragma map for width, height. We don't need fps
                    # as that one will receive the main class's pipeline
                    shader_as_texture.render_config(width = int(width), height = int(height), fps = None)

                    # Create a texture and fbo for this mapped shader, here is where we render to the fbo
                    # which is attached to the texture, and we use that texture in this main class
                    texture, fbo = shader_as_texture.construct_texture_fbo()

                    # Construct the shader we loaded
                    shader_as_texture.construct_shader(fragment_shader = loader_frag_shader)

                    # Append to the shaders as textures. We only do this for passing a pipeline to the mapped shader
                    self.shaders_as_textures.append(shader_as_texture)

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[len(self.textures.keys()) + 1] = [name, "shader", shader_as_texture.texture]

                # Video loader
                elif loader == "video":

                    # Get one VideoCapture
                    video = cv2.VideoCapture(value)

                    # Create a RGB texture for the video
                    texture = MMVShaderMGL.gl_context.texture((width, height), 3)

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[len(self.textures.keys()) + 1] = [name, "video", texture, video]
                    
                # Add the texture uniform values
                marker = "///add_uniform"
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"\n// Texture\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform sampler2D {name};\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform int {name}_width;\n{marker}")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform int {name}_height;\n{marker}\n")
                fragment_shader_prefix = fragment_shader_prefix.replace(f"{marker}", f"uniform vec2 {name}_resolution;\n{marker}\n")
    
                # The attributes we'll put into the previous values
                assign_static_uniforms += [
                    [f"{name}_width", int(width)],
                    [f"{name}_height", int(height)],
                    [f"{name}_resolution", (int(width), int(height))],
                ]

        # # Get #pragma includes

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma include")
        
        # Simple regex and get every match with findall
        regex = r"([ ]+)?#pragma include ([\w/. -]+)"
        found = re.findall(regex, fragment_shader, re.MULTILINE)

        logging.info(f"{debug_prefix} Regex findall says: {found}")
 
        # For each #pragma include we found
        for mapping in found:
            identation, include = mapping

            # If this include was already made then no need to do it again.
            if include in self.included_files:
                logging.info(f"{debug_prefix} File / path already included [{include}]")
                continue
            
            # Mark that this was already included
            self.included_files.append(include)

            # This will replace this line (we build back)
            replaces = f"{identation}#pragma include {include}"    

            # # Attempt to find the file on the included directories

            look_for_in_included_directories = f"{include}.glsl"
            logging.info(f"{debug_prefix} Checking on include directories for [{look_for_in_included_directories}]")
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

        # We parsed the body and added to the prefix stuff that was defined so merge everything together
        fragment_shader = f"{fragment_shader_prefix}\n{fragment_shader}"

        # Pretty print / log
        s = "-" * shutil.get_terminal_size()[0]
        print(s)
        logging.info(f"{debug_prefix} Fragment shader is:\n{fragment_shader}")
        print(s)
        logging.info(f"{debug_prefix} Vertex shader is:\n{vertex_shader}")
        print(s)

        # # Construct the shader

        # Create a program with the fragment and vertex shader
        self.program = MMVShaderMGL.gl_context.program(fragment_shader = fragment_shader, vertex_shader = vertex_shader)

        # Get a texture bound to the FBO
        self.texture, self.fbo = self.construct_texture_fbo()
 
        # Create one VAO on the program with the coordinate info
        self.vao = MMVShaderMGL.gl_context.vertex_array(
            self.program, [(
                # Fill the whole screen
                self.fullscreen_buffer,

                # Expect three pairs of floats
                "2f 2f 2f",

                # What the floats means
                "in_pos", "in_opengl_uv", "in_shadertoy_uv"
            )],

            # Ignore unused vars, like, when we don't ever touch one uv coordinate system just 
            # keep going and don't blame the user we're not binding to an used attribute
            skip_errors = True
        )

        # Assign the uniforms to blank value
        for name, value in assign_static_uniforms:
            uniform = self.program.get(name, FakeUniform())
            uniform.value = value

    # # Loop functions, routines

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
        for shader_as_texture in self.shaders_as_textures:
            self.pipe_pipeline(pipeline = pipeline, target = shader_as_texture)
            shader_as_texture.render(pipeline = pipeline)

        # Pipe the pipeline to self
        self.pipe_pipeline(pipeline = pipeline, target = self)

        # Render to the FBO using this VAO
        self.fbo.use()
        self.fbo.clear()

        # The location is the dict index, the texture info is [name, loader, object]
        for location, texture_info in self.textures.items():
            # Unpack
            name, loader, tex_obj = texture_info

            try:
                # Read the next frame of the video
                if loader == "video":

                    # We'll only have a fourth element that is video if loader is video
                    video = texture_info[3]
                    ok, frame = video.read()

                    # Can't read, probably out of frames?
                    if not ok:  # cry
                        # Reset to frame 0
                        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        # Read again
                        ok, frame = video.read()
                    
                    # Flip the image TODO: flip in GLSL by inverting uv? Also interpret BGR as RGB?
                    frame = cv2.flip(frame, 0)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    tex_obj.write(frame)

                # Set the location we'll expect this texture
                self.program[name] = location
                
                # Use it
                tex_obj.use(location = location)
            
            # Texture wasn't used, should error out on self.program[name]
            except KeyError:
                pass

        # Render to this class FBO
        self.vao.render(mode = moderngl.TRIANGLE_STRIP)

    # Iterate through this class instance as a generator for getting the 
    def next(self, custom_pipeline = {}):

        # Set the pipeline attributes
        self.pipeline["mmv_frame"] += 1
        self.pipeline["mmv_time"] = round((self.pipeline["mmv_frame"] / self.fps), 3)
        self.pipeline["mmv_resolution"] = (self.width, self.height)

        # Assign user custom pipelines.
        # NOTE: Don't forget to write (uniform (type) name;) on the GLSL file
        # and also be sure that the name is unique, we don't check this here due Python performance
        for key, value in custom_pipeline.items():
            self.pipeline[key] = value

        # print(self.pipeline)
        self.render(pipeline = self.pipeline)
            
    # Read from the current FBO, return the bytes
    def read(self):
        return self.fbo.read()
    
    # Write directly into a subprocess (FFmpeg, FFplay)
    # Use this for speeds preferably
    def read_into_subprocess_stdin(self, target_stdin):
        target_stdin.write(self.fbo.read())
