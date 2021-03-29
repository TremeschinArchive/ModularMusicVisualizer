import time
import mmv
import os


def main():
    interface = mmv.MMVPackageInterface()
    shader_interface = interface.get_shader_interface()

    # ShaderMaker Interface

    shadermaker = shader_interface.get_mmv_shader_maker()(
        working_directory = interface.shaders_dir, name = "Prototype test shader"
    )
    BlockOfCode = shadermaker.block_of_code

    # Test add stuff

    # shadermaker.add_function(function = BlockOfCode(
    # """\
    # vec4 demo(vec2 uv) {
    #     return vec4(uv.x, uv.y, 0.0, 1.0);
    # }""", scoped = False, name = "Add test function"
    # ))

    # image = shadermaker.transformations.image(
    #     image = "background"
    # )
    # image.set_name("Original image")
    # image.disable()

    # print(image)
    # print("Extend image with image")

    # copied_image = image.clone()
    # copied_image.unscope()
    # copied_image.set_name("Cloned and unscoped image, set as extensions")
    # image.extend(copied_image)
    # copied_image.scope()

    # shadermaker.add_transformation(transformation = image)

    # # # Test shadermaker.transformations and stuff

    # # Alpha composite

    shadermaker.add_image_mapping(name = "background", path = f"{interface.assets_dir}/free_assets/glsl_default_background.jpg")
    shadermaker.add_include(include = "mmv_specification")

    background_layer = shadermaker.transformations.get_texture(texture_name = "background", uv = "shadertoy_uv", assign_to_variable = "processing")
    alpha_composite = shadermaker.transformations.alpha_composite(new = "processing")
    background_layer.extend(alpha_composite)

    shadermaker.add_transformation(transformation = background_layer)

    # Build final shader
    shadermaker.build_final_shader()

    # Save to file
    saveto = f"{interface.runtime_dir}{os.path.sep}{shadermaker.name}-frag.glsl"
    shadermaker.save_shader_to_file(saveto)
    path = shadermaker.get_path()

    # # View realtime code

    mgl = shader_interface.get_mmv_shader_mgl()(master_shader = True)
    mgl.include_dir(f"{interface.shaders_dir}{os.path.sep}include")
    mgl.target_render_settings(width = 1920, height = 1080, ssaa = 1, fps = 60)
    mgl.mode(window_class = "glfw", strict = False, vsync = False, msaa = 4)

    mgl.load_shader_from_path(path)

    while True:
        start = time.time()
        mgl.next()
        mgl.update_window()
        if mgl.window_handlers.window_should_close:
            break
        while (time.time() - start) < (1 / 60):
            time.sleep(1 / (60 * 100))

if __name__ == "__main__":
    main()