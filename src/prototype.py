from mmv.sombrero.sombrero_constructor import *
from mmv.sombrero.sombrero_shader import *
from PIL import Image
import time
import mmv
import os

FPS = 60

def main():
    interface = mmv.MMVPackageInterface()
    sombrero_main = interface.get_sombrero()(mmv_interface = interface, master_shader = True)
    sombrero_main.configure(width = 1920, height = 1080, fps = FPS, ssaa = 1)
    sombrero_main.window.configure()

    blueprint = sombrero_main.new_child()
    blueprint.macros.load(interface.shaders_dir/"assets"/"background"/"blueprint.glsl")

    background = sombrero_main.new_child()
    background.macros.load(interface.shaders_dir/"assets"/"background"/"moving_image.glsl")
    background.macros.add_mapping(TextureImage(name = "background", path = interface.assets_dir/"free_assets"/"glsl_default_background.jpg"))

    rain = sombrero_main.new_child()
    rain.macros.load(interface.shaders_dir/"assets"/"fx"/"rain.glsl")

    vignetting = sombrero_main.new_child()
    vignetting.macros.load(interface.shaders_dir/"assets"/"pfx"/"vignetting.glsl")

    hud = sombrero_main.new_child()
    hud.macros.load(interface.shaders_dir/"sombrero"/"default_hud.glsl")

    # # Alpha composite

    layers = [blueprint, background, rain, vignetting, hud]
    sombrero_main.macros.alpha_composite(layers, gamma_correction = True)

    # # Render
    
    while True:
        start = time.time()

        sombrero_main.next()
        if sombrero_main.window.window_should_close: break

        # Vsync
        while time.time() - start < 1 / FPS: time.sleep(1/(2*FPS))

        # FPS
        # print("\r" + str(sombrero_main.pipeline["mFrame"]), end = "", flush = True)
