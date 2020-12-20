import mmvshader
import os

mmv = mmvshader.MMVShaderMain()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

mmv.mpv.input_output(
    input_video = f"{THIS_DIR}/data/source.mkv",
    output_video = "out.mkv"
)
mmv.mpv.resolution(width = 1280, height = 720)
mmv.mpv.run()