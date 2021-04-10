"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Preprocessor for MMVShaderMGL

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

import mmv.mmvshader.mmv_shader_mgl as MMVShaderMGL
from ast import literal_eval
from pathlib import Path
from PIL import Image
import numpy as np
import logging
import os


class MMVShaderMGLPreprocessor:
    def __init__(self, mmv_shader_mgl):
        self.mmv_shader_mgl = mmv_shader_mgl
        self.to_flip_or_not_to_flip = False
        self.include_directories = []
        self.reset()
        
    def reset(self):
        # When we use [#pragma include name/path] we have the option to put a directory or a name in there, 
        # we search for these paths for a file that is named [name.glsl] so we don't have to pass the full
        # path and make this act kinda like a (lazy | compact) method of including other shaders.
        #
        # The included files dir is for files we already included so we don't include twice and cause
        # redefinition errors
        self.included_files_once = []

    # Generator that gives us dictionaries on line matchings
    #
    # For each line if "//#mmv" is on the line keep reading until finds }
    # We use a comment because we avoid GLSL treating our map as their syntax,
    # this is mostly likely to fail on Windows by the look of things if we don't comment stuff.
    #
    # Yields the size of the indent, the content of the line as dict and the original line itself
    def __match_mmv_line_yield_dictionary(self, full_file_string) -> list:
        debug_prefix = "[MMVShaderMGLPreprocessor.__match_mmv_line_yield_dictionary]"

        # For matching multi line dictionaries
        partially_matched = []
        trigger_keep_reading = False

        # Iterate on all lines
        for original_line in full_file_string.split("\n"):

            # We have some work to do, mark as to keep reading and get indentation
            if "//#mmv" in original_line:
                trigger_keep_reading = True
                indent, _ = original_line.split("//#mmv")
            
            # If we are on a match
            if trigger_keep_reading:

                # Replace commands #mmv, also remove comments //
                line = original_line.replace("//#mmv", "").replace("//", "")

                # Add to the partially matched this "cleaned" line from MMV's syntax
                partially_matched.append(line)

            # If we are still reading stuff (or first pass) and "}"
            # is present on the line then that means to stop
            if ("}" in original_line and trigger_keep_reading):

                # Join every line with spaces, replacing newlines
                partially_matched = ' '.join([p.replace("\n", "") for p in partially_matched if p])

                # Remove trailing whitespaces
                partially_matched = partially_matched.strip()

                # String -> dictionary
                content = literal_eval(partially_matched)

                # Reset variables
                partially_matched = []
                trigger_keep_reading = False

                # Yield stuff as specified
                yield [len(indent), content, original_line]

    # Add a directory to the list of directories to include, note that this will recursively add this
    # include dir to the shaders as textures mapped
    def include_dir(self, path):
        debug_prefix = "[MMVShaderMGLPreprocessor.include_dir]"
        
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
        for index in self.mmv_shader_mgl.contents:
            if self.mmv_shader_mgl.contents[index]["loader"] == "shader":
                self.mmv_shader_mgl.contents[index]["shader_as_texture"].include_dir(path = path)

    # Parse a shader, load stuff on MMVShaderMGL main file
    def parse(self, shader):
        debug_prefix = "[MMVShaderMGLPreprocessor.parse]"

        # The static uniforms we'll assign the values to (eg. image, video, shader resolutions)
        # This already includes the type (vec2, sampler2D or what)
        new_uniforms = []

        logging.info(f"{debug_prefix} Iterating on Preprocessor matches")

        # For each mapping, get its values and assign stuff
        for indent_length, content, original_line in self.__match_mmv_line_yield_dictionary(shader):
            logging.info(f"{debug_prefix} Match [indent={indent_length}] [content={content}]")

            # Standard stuff, required or not
            action = content.get("type", None)
            value = value = content.get("value", None)
            loader = content.get("loader", None)
            name = content.get("name", None)
            mode = content.get("mode", None)

            # Width, Height, Depth
            width = content.get("width", None)
            height = content.get("height", None)
            depth = content.get("depth", None)

            # Textures mipmaps, anisotropy
            mipmaps = content.get("mipmaps", True)
            mipmaps_max_level = content.get("mipmaps_max_level", 2000)
            anisotropy = content.get("anisotropy", 1.0)

            # Repeat stuff
            repeat_x = content.get("repeat_x", True)
            repeat_y = content.get("repeat_y", True)

            # Shader as texture
            fragment_shader_path = content.get("fragment_shader_path", None)
            vertex_shader_path = content.get("vertex_shader_path", None)
            geometry_shader_path = content.get("geometry_shader_path", None)

            # Didn't find any actions
            if action is None:
                logging.warning(f"{debug_prefix} Mapping does nothing, no \"type\" specified")

            # Assign name to this shader
            elif action == "name":
                self.name = content["value"]
                logging.info(f"{debug_prefix} Set name to [{self.name}]")

            # To flip or not to flip, that is the question
            elif action == "flip":
                self.flip = content["value"]
                logging.info(f"{debug_prefix} Set flip to [{self.flip}]")
                self.mmv_shader_mgl.__build_coordinates()

            # Include some file from a absolute path or on the includes folder
            elif action == "include":
                include = value

                logging.info(f"{debug_prefix} Got instruction to include some file value [{include}] mode [{mode}]")

                # If this include was already made then no need to do it again.
                # mode "multiple" bypasses this
                if mode == "once":
                    if include in self.included_files_once:
                        logging.info(f"{debug_prefix} File / path already included [{include}]")
                        continue
                
                # Mark that this was already included
                self.included_files_once.append(include)

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
                                    include_other_glsl_data.append(f"{' ' * indent_length}{line}")

                                # Join the indented lines
                                include_other_glsl_data = ''.join(include_other_glsl_data)

                                # Replace ONCE, since the condition previously said we're not on once mode or
                                # we are on once mode and this is the first pass
                                shader = shader.replace(original_line, include_other_glsl_data, 1)

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
                shader = shader.replace(original_line, include_other_glsl_data, 1)  # Replace ONCE

            # Map something
            elif action == "map":
                logging.info(f"{debug_prefix} Action is to map something")
                    
                # Error assertion, valid loader and path
                loaders = ["image", "video", "shader", "dynshader", "pipeline_texture", "include"]
                assert loader in loaders, f"Loader [{loader}] not implemented in loaders [{content}]"

                # We'll map one texture to this shader, either a static image, another shader or a video
                # we do create and store the shader and video objects so we render or get the next image later on before using
                textures_related = ["image", "shader", "dynshader", "video", "pipeline_texture"]

                # Loader type will be applied in some direct texture method
                if loader in textures_related:
                    logging.info(f"{debug_prefix} Loader [{loader}] is in textures related {textures_related}")

                    # Image loader, load image, convert to RGBA, create texture with target resolution, assign texture
                    if loader == "image":

                        # Load the image, get width and height for the texture size
                        img = Image.open(value).convert("RGBA")

                        # Set to the read width and height based on if width or height are None
                        if (width is None):
                            width = img.size[0]
                        if (height is None):
                            height = img.size[1]

                        # Convert image to bytes and upload the texture to the GPU
                        logging.info(f"{debug_prefix} Uploading image texture [{value}] to the GPU in RGBA mode, assign on textures dictionary")
                        texture = self.mmv_shader_mgl.gl_context.texture((width, height), 4, img.tobytes())

                        # Mipmaps
                        if mipmaps:
                            logging.info(f"{debug_prefix} Building mipmaps..")
                            texture.build_mipmaps(max_level = mipmaps_max_level)
                            logging.info(f"{debug_prefix} Done!")

                        # Anisotropy
                        logging.info(f"{debug_prefix} Setting anisotropy suggested level to [{anisotropy}]")
                        texture.anisotropy = anisotropy

                        # Repeat
                        texture.repeat_x = repeat_x
                        texture.repeat_y = repeat_y

                        assign_index = len(self.mmv_shader_mgl.contents.keys())

                        # Assign the name, type and texture to the textures dictionary
                        self.mmv_shader_mgl.contents[assign_index] = {
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
                        texture = self.mmv_shader_mgl.gl_context.texture((width, height), int(depth), dtype = "f4")
                        texture.anisotropy = anisotropy

                        # Repeat
                        texture.repeat_x = repeat_x
                        texture.repeat_y = repeat_y
                        
                        # Write zeros to texture, there is no guarantee the buffer is clean
                        texture.write(np.zeros((width, height, depth), dtype = np.float32))

                        # Assign the name, type and texture to the textures dictionary
                        assign_index = len(self.mmv_shader_mgl.contents.keys())
                        
                        self.mmv_shader_mgl.contents[assign_index] = {
                            "name": name, 
                            "loader": "texture",
                            "texture": texture
                        }

                        # Put into the writable textures dictionary
                        self.mmv_shader_mgl.writable_textures[name] = assign_index
                    
                    # Add shader as texture element
                    # shader is strict resolution
                    # dynshader adapts to the viewport
                    elif (loader == "shader") or (loader == "dynshader"):

                        # We need an target render size if it's all but dynshader
                        if loader == "dynshader":
                            logging.info(f"{debug_prefix} Loader is dynamic shader, set width and height to this class's width and height")
                            width, height = self.mmv_shader_mgl.width, self.mmv_shader_mgl.height
                        else:
                            # Strict "shader" mode must have width and height
                            assert (width is not None) and (height is not None), "Width or height shouldn't be null for standard shader mode"
                            logging.info(f"{debug_prefix} Loader is strict shader, set width and height to specified one [{width}x{height}]")

                            # Convert to int the width and height
                            width, height = int(width), int(height)
                            
                        # Load frag shader
                        if fragment_shader_path == "NULL":
                            logging.info(f"{debug_prefix} Fragment shader path is NULL, use NULL shader")
                            loader_frag_shader = MMVShaderMGL.MMV_MGL_NULL_FRAGMENT_SHADER
                        else:
                            assert fragment_shader_path is not None, "Fragment shader must be set!!"
                            logging.info(f"{debug_prefix} Load fragment shader in path [{fragment_shader_path}]")
                            loader_frag_shader = Path(fragment_shader_path).read_text()

                        # Load vertex shader
                        if vertex_shader_path == "None":
                            logging.info(f"{debug_prefix} User default Vertex Shader")
                            loader_vertex_shader = MMVShaderMGL.MMV_MGL_DEFAULT_VERTEX_SHADER
                        else:
                            logging.info(f"{debug_prefix} Load vertex shader in path [{vertex_shader_path}]")
                            loader_vertex_shader = Path(vertex_shader_path).read_text()

                        # Load geometry shader if any
                        if geometry_shader_path != "None":
                            logging.info(f"{debug_prefix} Load geometry shader in path [{geometry_shader_path}]")
                            loader_geometry_shader = Path(geometry_shader_path).read_text()
                        else: loader_geometry_shader = None

                        # # Construct a class of this same type of the master shader, use the same context

                        # To flip or not to flip is a bit tricky of a question, this worked for me..
                        flip = not self.mmv_shader_mgl.flip
                        # self.to_flip_or_not_to_flip = not self.to_flip_or_not_to_flip
                        shader_as_texture = MMVShaderMGL.MMVShaderMGL(flip = self.to_flip_or_not_to_flip, gl_context = self.mmv_shader_mgl.gl_context)

                        # Add included dirs
                        for directory in self.include_directories:
                            shader_as_texture.include_dir(directory)

                        # Set the render configuration on the #pragma map for width, height. We don't need fps
                        # as that one will receive the main class's pipeline
                        shader_as_texture.target_render_settings(width = int(width), height = int(height), ssaa = self.mmv_shader_mgl.ssaa, fps = None)

                        # Construct the shader we loaded
                        shader_as_texture.construct_shader(
                            fragment_shader = loader_frag_shader,
                            vertex_shader = loader_vertex_shader,
                            geometry_shader = loader_geometry_shader,
                        )

                        # Anisotropy
                        shader_as_texture.texture.anisotropy = anisotropy

                        # Next available id
                        assign_index = len(self.mmv_shader_mgl.contents.keys())

                        # Assign the name, type and texture to the textures dictionary
                        self.mmv_shader_mgl.contents[assign_index] = {
                            "shader_as_texture": shader_as_texture,
                            "dynamic": loader == "dynshader",
                            "loader": "shader",
                            "name": name,
                        }

                    # Video loader
                    elif loader == "video":
                        import cv2

                        # Get one VideoCapture
                        video = cv2.VideoCapture(value)

                        # Create a RGB texture for the video
                        texture = self.mmv_shader_mgl.gl_context.texture((width, height), 3)
                        texture.anisotropy = anisotropy

                        # CV2 reads stuff as BGR rather than RGB so we have to revert those
                        texture.swizzle = 'BGR'

                        # Next available id
                        assign_index = len(self.mmv_shader_mgl.contents.keys())

                        # Assign the name, type and texture to the textures dictionary
                        self.mmv_shader_mgl.contents[assign_index] = {
                            "name": name,
                            "loader": "video",
                            "texture": texture,
                            "capture": video,
                        }
                        
                    # Add the texture uniform values
                    marker = "//#shadermgl add_uniforms"
                    shader = shader.replace(f"{marker}", f"\n// Texture\n{marker}")
                    shader = shader.replace(f"{marker}", f"uniform sampler2D {name};\n{marker}")
                    shader = shader.replace(f"{marker}", f"uniform int {name}_width;\n{marker}")
                    shader = shader.replace(f"{marker}", f"uniform int {name}_height;\n{marker}\n")
                    shader = shader.replace(f"{marker}", f"uniform vec2 {name}_resolution;\n{marker}\n")
        
                    # The attributes we'll put into the previous values
                    new_uniforms += [
                        [f"{name}_width", int(width)],
                        [f"{name}_height", int(height)],
                        [f"{name}_resolution", (int(width), int(height))],
                    ]

                    logging.info(f"{debug_prefix} New uniforms to add: {new_uniforms}")
    
        # Return info, whatnot
        return {
            "shader": shader,
            "new_uniforms": new_uniforms
        }