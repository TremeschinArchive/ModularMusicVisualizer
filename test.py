import mmv

processing = mmv.mmv()

processing.performance(
    multiprocessed=True,
    workers=2
)

processing.quality(
    width=1280,
    height=720,
    fps=60
)

processing.input_audio("mmv/banjo.ogg")
processing.output_video("demorun.mkv")

image = processing.image_object()

image.configure.init_animation_layer()
image.configure.load_image("background.jpg")
image.configure.resize_to_video_resolution()

image.configure.add_path_point(0, 0)
image.configure.simple_add_path_modifier_shake(20)

image.configure.simple_add_linear_blur(intensity="medium")
image.configure.simple_add_linear_resize(intensity="high")
# image.configure.simple_add_swing_rotation()

processing.add(image, layer=0)


visualizer = processing.image_object()
visualizer.configure.init_animation_layer()
visualizer_size = min(processing.resolution)
visualizer.configure.simple_add_visualizer_circle(
    width=visualizer_size, height=visualizer_size,
    minimum_bar_size=100,
    mode="symetric",
    fft_smoothing=2,
    subdivide=4
)

# Center the visualizer
visualizer.configure.add_path_point(
    processing.width // 2 - (visualizer_size / 2),
    processing.height // 2 - (visualizer_size / 2),
)

# visualizer.configure.simple_add_linear_blur(intensity="high")
visualizer.configure.simple_add_linear_resize(intensity="high")

visualizer.configure.simple_add_path_modifier_shake(
    shake_max_distance=5,
    x_smoothness=0.01,
    y_smoothness=0.02
)

processing.add(visualizer, layer=3)


processing.run()


