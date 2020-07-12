from mmv.utils import Miscellaneous
from mmv.mmvimage import MMVImage
from mmv.main import MMVMain
from mmv.utils import Utils
import sys
import os


class mmv:
    def __init__(self):
        Miscellaneous()
        self.main = MMVMain()
        self.utils = Utils()
        self.main.setup(cli=False)

    def performance(self, multiprocessed=False, workers=4):
        self.main.context.multiprocessed = multiprocessed
        self.main.context.multiprocessing_workers = workers
    
    def quality(self, width=1280, height=720, fps=60):
        self.main.context.width = width
        self.main.context.height = height
        self.main.context.fps = fps
    
    def preset(self, preset):
        if not preset in self.main.context.presets:
            print("Preset unmatched [%s] --> " % (preset, self.main.context.presets))
            sys.exit(-1)
        self.main.context.preset(preset)
    
    def add_input_audio(self, path):
        if not os.path.exists(path):
            print("Input audio path does not exist [%s]" % path)
            sys.exit(-1)
        self.main.context.input_file = path
        self.main.setup_input_audio_file()
    
    def run(self):
        self.main.run()
    
    def image_object(self):
        return MMVImage(self.main.context)
    
    def add(self, item, layer=0):
        if self.utils.is_matching_type([item], [MMVImage]):
            self.main.core.mmvanimation.content[layer].append(item)
