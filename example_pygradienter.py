


import mmv
processing = mmv.mmv()

gr = processing.pygradienter()

gr.config.resolution(200, 200)
gr.config.n_images(1)

gr.generate("simple_smooth")
