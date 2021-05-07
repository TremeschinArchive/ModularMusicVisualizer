from mmv.sombrero.sombrero_shader import *
from pathlib import Path
from array import array
import numpy as np


class FullScreenConstructor:
    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl
        self.vertex_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"rectangles_vertex.glsl").read_text()
        self.geometry_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"rectangles_geometry.glsl").read_text()
        self.num_vertices = 4
        self.buffer = self.sombrero_mgl.gl_context.buffer(reserve = 16)
        self.buffer.write(array("f", [0, 0, 2, 2]))
        self.once_returned_vao = False
    
    def treat_fragment_shader(self, sombrero_shader):
        io_placeholder = sombrero_shader.IOPlaceHolder
        IO("vec2", "opengl_uv", prefix = False, mode = "i")(io_placeholder)
        IO("vec2", "shadertoy_uv", prefix = False, mode = "i")(io_placeholder)
        IO("vec4", "fragColor", prefix = False, mode = "o")(io_placeholder)

    def vao(self):
        if self.once_returned_vao: return
        self.once_returned_vao = True
        return [(self.buffer, "2f 2f", "in_pos", "in_size"),]

    def next(self):
        pass



class PianoRollConstructor:
    def __init__(self, sombrero_mgl, piano_roll, expect, maxkeys = 500):
        self.sombrero_mgl = sombrero_mgl
        self.piano_roll = piano_roll
        self.expect = expect
        self.vertex_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"piano_vertex.glsl").read_text()
        self.geometry_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"piano_geometry.glsl").read_text()
        self.buffer = self.sombrero_mgl.gl_context.buffer(reserve = 4 * 4 * maxkeys)
    
    def treat_fragment_shader(self, sombrero_shader):
        io_placeholder = sombrero_shader.IOPlaceHolder
        IO("vec2", "opengl_uv", prefix = False, mode = "i")(io_placeholder)
        IO("vec2", "shadertoy_uv", prefix = False, mode = "i")(io_placeholder)
        IO("int", "note", prefix = False, mode = "i", flat = True)(io_placeholder)
        IO("int", "velocity", prefix = False, mode = "i", flat = True)(io_placeholder)
        IO("int", "channel", prefix = False, mode = "i", flat = True)(io_placeholder)
        IO("int", "is_playing", prefix = False, mode = "i", flat = True)(io_placeholder)
        IO("int", "is_white", prefix = False, mode = "i", flat = True)(io_placeholder)
        IO("vec4", "fragColor", prefix = False, mode = "o")(io_placeholder)

    def vao(self):
        self.buffer.clear()

        instructions = self.piano_roll.generate_note_coordinates()

        if self.expect == "notes":
            draw = [attr for note in instructions["notes"] for attr in note]
            self.buffer.write(array("f", draw))
            self.num_vertices = 4 * len(instructions["notes"])

        return (self.buffer,
            "2f 2f 1f 1f 1f 1f 1f",
            "in_pos", "in_size", "in_note", "in_velocity", "in_channel", "in_is_playing", "in_is_white"
        ),

    def next(self):
        pass