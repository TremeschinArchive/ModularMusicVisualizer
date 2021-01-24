"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: 

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
import cv2
import sys
import re
import os

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Default shader vertex, just accepts an input position, places itself relative to the
# XY plane of the screen and gives us back an uv for the fragment shader
DEFAULT_VERTEX_SHADER = """\
#version 330

// Input / output of coordinates
in vec2 in_pos;
in vec2 in_uv;
out vec2 uv;

// Main function, only assign the position to itself and set the uv coordinate
void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    uv = in_uv;
}"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# MMV Specification
# We prefix every fragment shader with this, it's the declaration of uniforms and whatnot
# we also modify, add to it custom ones the user chose.
FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX = """\
#version 330

// Input and Output of colors
out vec4 fragColor;
in vec2 uv;

// MMV Specification
uniform int mmv_frame;
uniform float mmv_time;
uniform vec2 mmv_resolution;

uniform int do_flip;

///add_uniform"""


# Hello world of the fragment shaders
DEFAULT_FRAGMENT_SHADER = """\
void main() {
    fragColor = vec4(uv.x, uv.y, abs(sin(mmv_time/180.0)), 1.0);
}"""

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# When an uniform is not used it doesn't get initialized on the program
# so we .get(name, FakeUniform()) so we don't get errors here
class FakeUniform:
    value = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MMVShaderMGL:
    def __init__(self):
        debug_prefix = "[MMVShaderMGL.__init__]"

        # Create a headless OpenGL context  TODO: support for window mode (performance)?
        self.gl_context = moderngl.create_context(standalone = True)

        # The buffer that represents the 4 points of the screen and their
        # respective uv coordinate. GL center is the coordinate (0, 0) and each
        # edge is either 1 or -1 relative to its axis. We keep that because central rotation
        self.fullscreen_buffer = self.gl_context.buffer(array('f',
            [
            #  (   X,    Y   ) || (   U,    V   )
                -1.0,  1.0,         0.0,  0.0,
                -1.0, -1.0,         0.0,  1.0,
                 1.0,  1.0,         1.0,  0.0,
                 1.0, -1.0,         1.0,  1.0,
            ]
            # [
            # #  (   X,    Y   ) || (   U,    V   )
            #     -1.0,  1.0,        -1.0,  1.0,
            #     -1.0, -1.0,        -1.0, -1.0,
            #      1.0,  1.0,         1.0,  1.0,
            #      1.0, -1.0,         1.0, -1.0,
            # ]
        ))

        # Info we send to the shaders read only (uniforms)
        self.pipeline = {
            "mmv_time": 0,
            "mmv_frame": 0,
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
        (self.width, self.height, self.fps) = [None]*3

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
        texture = self.gl_context.texture((self.width, self.height), 4)

        # Create an FBO which is attached to that previous texture, whenever we render something
        # to this FBO after fbo.use()-ing it, the contents will be written directly on that texture
        # which we can bind to some location in other shader. This process is recursive
        fbo = self.gl_context.framebuffer(color_attachments = [texture])

        # Return the two created objects
        return [texture, fbo]

    # Create one context's program out of a frag and vertex shader, those are used together
    # with VAOs so we render to some FBO. 
    # Parses for #pragma map name=loader:value:WxH and creates the corresponding texture, binds to it
    # Also copies #pragma include <path.glsl> to this fragment shader
    def construct_shader(self, fragment_shader = DEFAULT_FRAGMENT_SHADER, vertex_shader = DEFAULT_VERTEX_SHADER):
        debug_prefix = "[MMVShaderMGL.construct_shader]"

        # The raw specification prefix, sets uniforms every one should have
        # we don't add just yet to the fragment shader because we can have some #pragma map
        # and we have to account for that before compiling the shader
        fragment_shader_prefix = FRAGMENT_SHADER_MMV_SPECIFICATION_PREFIX

        # # Parse the shader

        logging.info(f"{debug_prefix} Parsing the fragment shader for every #pragma map")

        # Regular expression to match #pragma map name=loader:/path/value;512x512
        # the ;512x512 is required for the image, video and shader loaders
        regex = r"#pragma map ([\w]+)=([\w]+):([\w/. -]+):?([0-9]+)?x?([0-9]+)?"
        found = re.findall(regex, fragment_shader)

        # The static uniforms we'll assign the values to (eg. image, video, shader resolutions)
        assign_static_uniforms = []

        # For each mapping
        for mapping in found:
            # Get the values we matched
            name, loader, value, width, height = mapping
            logging.info(f"{debug_prefix} Matched mapping [name={name}] [loader={loader}] [width={width}] [height={height}]")

            # Error assertion, valid loader and path
            loaders = ["image", "video", "shader", "include"]
            assert loader in loaders, f"Loader not implemented in loaders {loaders}"
            assert os.path.exists(value), f"Value of loader [{value}] is not a valid path"

            # We'll map one texture to this shader, either a static image, another shader or a video
            # we do create and store the shader and video objects so we render or get the next image later on before using
            if loader in ["image", "shader", "video"]:

                # We need an target render size
                assert (width != '') and (height != ''), "Width or height shouldn't be null, set WxH on pragma map with ;512x512"

                # Convert to int the width and height
                width = int(width)
                height = int(height)

                # Image loader
                if loader == "image":
                    # Load the image, get width and height for the texture size
                    img = Image.open(value).convert("RGBA")
                    width, height = img.size

                    # Convert image to bytes and upload the texture to the GPU
                    logging.info(f"{debug_prefix} Uploading texture to the GPU")
                    texture = self.gl_context.texture((width, height), 4, img.tobytes())

                    # Assign the name, type and texture to the textures dictionary
                    self.textures[len(self.textures.keys()) + 1] = [name, "texture", texture]
                    
                # Add shader as texture element
                elif loader == "shader":

                    # Read the shader we'll map
                    with open(value, "r") as f:
                        loader_frag_shader = f.read()

                    # Create one instance of this very own class
                    shader_as_texture = MMVShaderMGL()

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
                    texture = self.gl_context.texture((width, height), 3)

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

        # Get #pragma includes

        # Simple regex and get every match with findall
        regex = r"#pragma include ([\w/. -]+)"
        found = re.findall(regex, fragment_shader)

        # For each #pragma include we found
        for include in found:

            # This will replace this line (we build back)
            replaces = f"#pragma include {include}"
            
            # Error assertion, the path must exist
            assert os.path.exists(include), f"Value of #pragma include is not a valid path [{include}]"

            # Read the other shader data
            with open(include, "r") as f:
                include_other_glsl_data = f.read()

            # Replace the line on this fragment shader with the included other one
            fragment_shader = fragment_shader.replace(replaces, include_other_glsl_data)

        # We parsed the body and added to the prefix stuff that was defined so merge everything together
        fragment_shader = f"{fragment_shader_prefix}\n{fragment_shader}"

        # # Construct the shader

        # Create a program and return it
        self.program = self.gl_context.program(fragment_shader = fragment_shader, vertex_shader = vertex_shader)
        self.vao = self.gl_context.vertex_array(self.program, [(self.fullscreen_buffer, '2f 2f', 'in_pos', 'in_uv')])
        self.texture, self.fbo = self.construct_texture_fbo()
 
        # Assign the VAO
        self.vao = self.gl_context.vertex_array(self.program, [(self.fullscreen_buffer, '2f 2f', 'in_pos', 'in_uv')])

        # Assign the uniforms to blank value
        for name, value in assign_static_uniforms:
            uniform = self.program.get(name, FakeUniform())
            uniform.value = value

        # Pretty print / log
        s = "-" * shutil.get_terminal_size()[0]
        print(s)
        logging.info(f"{debug_prefix} Fragment shader is:\n{fragment_shader}")
        print(s)
        logging.info(f"{debug_prefix} Vertex shader is:\n{vertex_shader}")
        print(s)

    # Pipe a pipeline to a target that have a program attribute
    def pipe_pipeline(self, pipeline, target):
        debug_prefix = "[MMVShaderMGL.pipe_pipeline]"

        # Pass the pipeline values to the shader
        for key, value in pipeline.items():
            uniform = target.program.get(key, FakeUniform())
            uniform.value = value
            
    # Render this shader to the FBO recursively
    def render(self, pipeline, do_flip = True):
        debug_prefix = "[MMVShaderMGL.render]"

        pipeline["do_flip"] = -1 if do_flip else 1

        # Render every shader as texture recursively
        for shader_as_texture in self.shaders_as_textures:
            self.pipe_pipeline(pipeline = pipeline, target = shader_as_texture)
            shader_as_texture.render(pipeline = pipeline, do_flip = not do_flip)

        # Pipe the pipeline to self
        self.pipe_pipeline(pipeline = pipeline, target = self)

        # Render to the FBO using this VAO
        self.fbo.use()
        self.fbo.clear()

        # The location is the dict index, the texture info is [name, loader, object]
        for location, texture_info in self.textures.items():
            name = texture_info[0]
            loader = texture_info[1]
            tex_obj = texture_info[2]

            try:
                import time
                # Read the next frame of the video
                if loader == "video":

                    # We'll only have a fourth element that is video if loader is video
                    video = texture_info[3]
                    
                    ok, frame = video.read()

                    # Can't read, probably out of frames?
                    if not ok: 

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

        # Assign user custom pipelines
        for key, value in custom_pipeline.items():
            self.pipeline[key] = value

        # print(self.pipeline)
        self.render(pipeline = self.pipeline)
            
    # Read from the current FBO
    def read(self):
        return self.fbo.read()