from mmv.sombrero.sombrero_shader import *
from pathlib import Path
from array import array


class FullScreenConstructor:
    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl
        self.vertex_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"rectangles_vertex.glsl").read_text()
        self.geometry_shader = Path(self.sombrero_mgl.shaders_dir/"sombrero"/"constructors"/"rectangles_geometry.glsl").read_text()
        self.num_vertices = 4
        self.buffer = self.sombrero_mgl.gl_context.buffer(reserve = 16)
        self.buffer.write(array("f", [0.5, 0.5, 2, 2]))
        self.once_returned_vao = False
    
    def treat_fragment_shader(self, sombrero_shader):
        io_placeholder = sombrero_shader.IOPlaceHolder
        IO("vec2", "opengl_uv", prefix = False, mode = "i")(io_placeholder)
        IO("vec2", "shadertoy_uv", prefix = False, mode = "i")(io_placeholder)
        IO("vec4", "fragColor", prefix = False, mode = "o")(io_placeholder)

    def vao(self):
        if self.once_returned_vao: return
        self.once_returned_vao = True
        return [(self.buffer, "2f 2f", "in_position", "in_size"),]

    def next(self):
        pass
