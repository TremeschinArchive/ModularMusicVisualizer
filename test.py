import mmv

visualizer = mmv.mmv()

visualizer.add_input_audio("mmv/banjo.ogg")

image = visualizer.image_object()

image.configure.init_animation_layer()
image.configure.load_image("background.jpg")
image.configure.resize_to_video_resolution()

image.configure.add_path_point(0, 0)
image.configure.simple_add_path_modifier_shake(20)

image.configure.simple_add_linear_blur(intensity="medium")
image.configure.simple_add_linear_resize(intensity="medium")
image.configure.simple_add_swing_rotation()

visualizer.add(image)

visualizer.performance(
    multiprocessed=False,
    workers=2
)

visualizer.quality(
    width=1280,
    height=720,
    fps=60
)

visualizer.run()