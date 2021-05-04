from mmv.sombrero.sombrero_constructor import *
from mmv.sombrero.sombrero_shader import *
from PIL import Image
import numpy as np
import random
import time
import mmv
import os

FPS = 60

def main():
    interface = mmv.MMVPackageInterface()
    sombrero_main = interface.get_sombrero()(mmv_interface = interface, master_shader = True)
    sombrero_main.configure(width = 1920, height = 1080, fps = FPS, ssaa = 1)
    sombrero_main.window.create()

    # # Layers
    FFTSIZE = 1000

    # layers = [blueprint, background, music_bars, rain, vignetting, hud]
    layers = []

    scene = 0

    if scene == 0:
        blueprint = sombrero_main.new_child()
        blueprint.macros.load(interface.shaders_dir/"assets"/"background"/"blueprint.glsl")
        layers.append(blueprint)

        background = sombrero_main.new_child()
        background.macros.load(interface.shaders_dir/"assets"/"background"/"moving_image.glsl")
        background.macros.add_mapping(TextureImage(name = "background", path = interface.assets_dir/"free_assets"/"glsl_default_background.jpg"))
        layers.append(background)

        music_bars = sombrero_main.new_child()
        music_bars.macros.load(interface.shaders_dir/"assets"/"music_bars"/"circle_sectors.glsl")
        music_bars.macros.add_mapping(TextureImage(name = "logo", path = interface.assets_dir/".."/".."/".."/"repo"/"mmv_logo_alt_white.png"))
        music_bars.macros.add_mapping(TexturePipeline(name = "mmv_fft", width = FFTSIZE, height = 1, depth = 1))
        layers.append(music_bars)

    if scene == 1:
        tetration = sombrero_main.new_child()
        tetration.macros.load(interface.shaders_dir/"assets"/"background"/"fractals"/"tetration.glsl")
        tetration.macros.add_include(Include(interface.shaders_dir/"include"/"complex.glsl"))

        tetration_pfx = sombrero_main.new_child()
        tetration_pfx.macros.load_chain_dependent(interface.shaders_dir/"assets"/"pfx"/"1_layer"/"test.glsl", [tetration])

        layers.append(tetration_pfx)

    rain = sombrero_main.new_child()
    rain.macros.load(interface.shaders_dir/"assets"/"fx"/"rain.glsl")
    layers.append(rain)
    
    vignetting = sombrero_main.new_child()
    vignetting.macros.load(interface.shaders_dir/"assets"/"pfx"/"vignetting.glsl")
    layers.append(vignetting)

    hud = sombrero_main.new_child()
    hud.macros.load(interface.shaders_dir/"sombrero"/"default_hud.glsl")
    layers.append(hud)

    # # Alpha composite

    sombrero_main.macros.alpha_composite(layers, gamma_correction = True)

    # # Render
    while True:
        start = time.time()
        sombrero_main.write_pipeline_texture("mmv_fft", [100 * (0.3 + 0.2*np.sin(np.linspace(0, 20*2*3.1415, FFTSIZE) + time.time()))])

        sombrero_main.next()
        if sombrero_main.window.window_should_close: break

        # Vsync
        while time.time() - start < 1 / FPS: time.sleep(1/(1000*FPS))

        # FPS
        # print("\r" + str(sombrero_main.pipeline["mFrame"]), end = "", flush = True)
