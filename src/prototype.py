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

    background = sombrero_main.new_child()
    background.shader = background.macros.load(interface.shaders_dir/"assets"/"background"/"blueprint.glsl")
    background.finish()

    hud = sombrero_main.new_child()
    hud.shader = hud.macros.load(interface.shaders_dir/"sombrero"/"default_hud.glsl")
    hud.finish()

    # # Alpha composite

    layers = [background, hud]

    sombrero_main.shader = sombrero_main.macros.alpha_composite(layers, gamma_correction = True)
    sombrero_main.finish()

    while True:
        start = time.time()
        sombrero_main.next()
        # print("\r" + str(sombrero_main.pipeline["mFrame"]), end = "", flush = True)
        if sombrero_main.window.window_should_close: break
        while time.time() - start < 1 / FPS: time.sleep(1/(2*FPS))

