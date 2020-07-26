    def add_moving_background(self, shake=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 2*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": "15*X",
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background2.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake),
            self.context.height + (2 * shake),
            override=True
        )

        self.content[0].append(temp)
    
    def add_moving_video_background(self, shake=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 0.3*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": "13*X",
                },
                "video": {
                    "path": self.context.ROOT + os.path.sep + "vid.mkv",
                    "shake": shake
                }
            }
        }
        
        self.content[0].append(temp)

    def add_static_background(self, shake=0): 

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake),
            self.context.height + (2 * shake),
            override=True
        )

        self.content[0].append(temp)

    def add_layers_background(self, shake1=0, shake2=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake1, -shake1),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake1,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 4*X",
                    "arg_a": 0.04,
                },
                "blur": {
                    "activation": "max(5 - 15*X, 0)",
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "layers" + os.path.sep + "space.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake1),
            self.context.height + (2 * shake1),
            override=True
        )

        temp2 = MMVImage(self.context)
        temp2.path[0] = {
            "position": [
                Point(-shake2, -shake2),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake2,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 2*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": "15*X",
                }
            }
        }
        temp2.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "layers" + os.path.sep + "curtains.png",
            # convert_to_png=True
        )
        temp2.image.resize_to_resolution(
            self.context.width + (2 * shake2),
            self.context.height + (2 * shake2),
            override=True
        )

        self.content[0].append(temp)
        self.content[1].append(temp2)

    def add_logo(self, shake=0):
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(
                    self.context.width // 2 - (self.logo_size/2),
                    self.context.height // 2 - (self.logo_size/2)
                ),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.04,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 6*X",
                    "arg_a": 0.07,
                },
                "rotate": {
                    "object": SineSwing(6, 100)
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "logo" + os.path.sep + "logo.png",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.logo_size,
            self.logo_size,
            override=True
        )

        self.content[4] = [temp]

    def add_visualizer(self, shake=0):

        visualizer_size = self.context.height #int((600/1280)*self.context.width)
        
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(
                    self.context.width // 2 - (visualizer_size/2),
                    self.context.height // 2 - (visualizer_size/2)
                ),
                Shake({
                    "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
                    "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.04,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "1 + 8*X",
                    "arg_a": 0.14,
                },
                # "rotate": {
                #     "object": MMVModifierLinearSwing(10)
                # },
                # "blur": {
                #     "activation": "20*X",
                # },
                "visualizer": {
                    "object": MMVVisualizer(
                        self.context,
                        {
                            "type": "circle",
                            "mode": "symetric",
                            "width": visualizer_size,
                            "height": visualizer_size,
                            "minimum_bar_distance": self.logo_size//2,
                            "activation": {
                                "function": copy.deepcopy(self.functions.sigmoid),
                                "arg_a": 10,
                            },
                            "fourier": {
                                "interpolation": {
                                    "function": copy.deepcopy(self.interpolation.remaining_approach),
                                    "activation": "X",
                                    "arg_a": 0.25,
                                    "steps": math.inf
                                },
                                "fitfourier": {
                                    "fft_smoothing": 2,
                                    "subdivide": 4,
                                }
                            }
                        }
                    )
                }
            }
        }
        self.content[3].append(temp)
    
    def add_post_processing(self):
        vignetting_start = 900
        self.canvas.vignetting = vignetting_start
        self.canvas.post_processing[0] =  {
            "steps": math.inf,
            "modules": {
                "vignetting": {
                    "interpolation": copy.deepcopy(self.interpolation.remaining_approach),
                    "activation": "%s - 4000*X" % vignetting_start,
                    "arg_a": 0.09,
                    "minimum": 450,
                },
                # "glitch": {
                #     "activation": "min(max(0.1+X*3,0), 10)",
                #     "color_offset": True,
                #     "scan_lines": False,
                # }
            }
        }

    def add_particles_generator(self):        
        generator = MMVParticleGenerator(self.context)
        self.generators.append(generator)

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):

        self.logo_size = int((200/1280)*self.context.width)

        config = {
            "static_background": False,
            "moving_background": False,
            "layers_background": False,
            "moving_video_background": False,
            "logo": False,
            "visualizer": False,
            "add_post_processing": False,
            "particles": False
        }

        if config["moving_background"]:
            self.add_moving_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["static_background"]:
            self.add_static_background()
        
        if config["layers_background"]:
            self.add_layers_background(
                shake1 = int((20/1280) * self.context.width),
                shake2 = int((10/1280) * self.context.width)
            )
        
        if config["moving_video_background"]:
            self.add_moving_video_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["logo"]:
            self.add_logo()

        if config["visualizer"]:
            self.add_visualizer()
        
        if config["add_post_processing"]:
            self.add_post_processing()
        
        if config["particles"]:
            self.add_particles_generator()
