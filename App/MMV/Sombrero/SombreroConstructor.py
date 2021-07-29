from array import array
from pathlib import Path

import numpy as np
from MMV.Sombrero.SombreroShader import *


class FullScreenConstructor:
    def __init__(self, SombreroMain):
        self.SombreroMain = SombreroMain
        self.SombreroContext = self.SombreroMain.SombreroContext
        self.VertexShader = Path(self.SombreroMain.SombreroDir/"Constructors"/"RectanglesVertex.glsl").read_text()
        self.GeometryShader = Path(self.SombreroMain.SombreroDir/"Constructors"/"RectanglesGeometry.glsl").read_text()
        self.num_vertices = 4
        self.buffer = self.SombreroContext.OpenGL_Context.buffer(reserve=16)
        self.buffer.write(array("f", [0, 0, 2, 2]))
        self.once_returned_vao = False
    
    def TreatFragmentShader(self, SombreroShader):
        io_placeholder = SombreroShader.IOPlaceHolder
        IO("vec2", "OpenGLUV", prefix = False, mode = "i")(io_placeholder)
        IO("vec2", "ShaderToyUV", prefix = False, mode = "i")(io_placeholder)
        IO("vec4", "fragColor", prefix = False, mode = "o")(io_placeholder)

    def vao(self):
        if self.once_returned_vao: return
        self.once_returned_vao = True
        return [(self.buffer, "2f 2f", "InPos", "InSize"),]

    def next(self):
        pass



class PianoRollConstructor:
    def __init__(self, SombreroMain, piano_roll, expect, maxkeys = 500):
        self.SombreroMain = SombreroMain
        self.SombreroContext = self.SombreroMain.SombreroContext
        self.piano_roll = piano_roll
        self.expect = expect
        self.VertexShader = Path(self.SombreroMain.SombreroDir/"Constructors"/"PianoVertex.glsl").read_text()
        self.GeometryShader = Path(self.SombreroMain.SombreroDir/"Constructors"/"PianoGeometry.glsl").read_text()
        self.buffer = self.SombreroContext.OpenGL_Context.buffer(reserve = 9 * 4 * maxkeys)
    
    def TreatFragmentShader(self, SombreroShader):
        io_placeholder = SombreroShader.IOPlaceHolder
        IO("vec2", "OpenGLUV", prefix = False, mode = "i")(io_placeholder)
        IO("vec2", "ShaderToyUV", prefix = False, mode = "i")(io_placeholder)
        IO("float", "note", prefix = False, mode = "i")(io_placeholder)
        IO("float", "velocity", prefix = False, mode = "i")(io_placeholder)
        IO("float", "channel", prefix = False, mode = "i")(io_placeholder)
        IO("float", "IsPlaying", prefix = False, mode = "i")(io_placeholder)
        IO("float", "IsWhite", prefix = False, mode = "i")(io_placeholder)
        IO("vec4", "fragColor", prefix = False, mode = "o")(io_placeholder)

    def vao(self):
        self.buffer.clear()

        instructions = self.piano_roll.generate_note_coordinates()

        draw = [attr for note in instructions[self.expect] for attr in note]
        self.buffer.write(array("f", draw))
        self.num_vertices = 4 * len(instructions[self.expect])

        return (self.buffer,
            "2f 2f 1f 1f 1f 1f 1f",
            "InPos", "InSize", "InNote", "InVelocity", "InChannel", "InIsPlaying", "InIsWhite"
        ),

    def next(self):
        pass