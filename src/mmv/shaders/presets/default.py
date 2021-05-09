from mmv.sombrero.sombrero_constructor import *
from mmv.sombrero.sombrero_shader import *

def generate(context):
    layers = []

    background = context.new_shader()
    background.macros.load(context.shaders_dir/"sombrero"/"menu.glsl")
    layers.append(background)

    context.render_layers(layers, gamma_correction = True, HUD = True)
