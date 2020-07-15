import mmv

processing = mmv.mmv()

processing.performance(
    multiprocessed=True,
    workers=6
)

processing.quality(
    width=1280,
    height=720,
    fps=60
)

# #
processing.assets_dir("assets/free_assets")
processing.create_pygradienter_asset(
    "particles",
    150, 150,
    True
)
# #

exit()

processing.input_audio("mmv/banjo.ogg")
processing.output_video("demorun.mkv")

image = processing.image_object()

image.configure.init_animation_layer()
image.configure.load_image("assets/background.jpg")
image.configure.resize_to_video_resolution()

image.configure.add_path_point(0, 0)
image.configure.simple_add_path_modifier_shake(20)

image.configure.simple_add_linear_blur(intensity="medium")
image.configure.simple_add_linear_resize(intensity="high")
# image.configure.simple_add_swing_rotation()

processing.add(image, layer=0)


logo_size = 200

logo = processing.image_object()

logo.configure.init_animation_layer()
logo.configure.load_image("assets/tremx_assets/logo/logo.png")
logo.configure.resize_to_resolution(logo_size, logo_size, override=True)

logo.configure.add_path_point(
    processing.width // 2 - (logo_size/2),
    processing.height // 2 - (logo_size/2)
)

logo.configure.simple_add_linear_resize(intensity="custom", activation="1+7*X")
logo.configure.simple_add_swing_rotation()

processing.add(logo, layer=4)


visualizer = processing.image_object()
visualizer.configure.init_animation_layer()
visualizer_size = min(processing.resolution)
visualizer.configure.simple_add_visualizer_circle(
    width=visualizer_size, height=visualizer_size,
    minimum_bar_size=logo_size//2,
    mode="symetric",
    responsiveness=0.25,
    pre_fft_smoothing=2,
    pos_fft_smoothing=0,
    subdivide=0
)

# Center the visualizer
visualizer.configure.add_path_point(
    processing.width // 2 - (visualizer_size / 2),
    processing.height // 2 - (visualizer_size / 2),
)

# visualizer.configure.simple_add_linear_blur(intensity="high")
visualizer.configure.simple_add_linear_resize(intensity="custom", activation="1+8*X")

visualizer.configure.simple_add_path_modifier_shake(
    shake_max_distance=5,
    x_smoothness=0.01,
    y_smoothness=0.02
)

processing.add(visualizer, layer=3)


processing.run()


