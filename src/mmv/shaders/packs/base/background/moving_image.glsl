
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);
    vec2 stuv_all = mGetSTUVAll();
    vec2 gluv_all = mGetGLUVAll();

    // Displacement stuff for organic movement
    vec2 low_freq_shake = vec2(cos(mTime*5.0/1.5), sin(mTime*8.0/1.5)) / 180.0;
    vec2 high_freq_shake = vec2(cos(mTime*10.0/1.3), sin(mTime*16.0/1.3)) / 300.0;
    vec2 offset = vec2(sin(mTime/7.135135), cos(mTime/4.523894)) / 20.0;

    // Scale and angle
    float scale = 2.2;
    float angle = sin(mTime)/80.0;

    // Linear transformation on where to get the texture of the image
    vec2 get_image_uv = gluv_all;
    get_image_uv += low_freq_shake + high_freq_shake + offset;

    // Blit image
    col += mBlitImage(
        col, background, // NOTE: We expect a "background" sampler2D mapped!
        background_resolution, // res
        get_image_uv, // uv
        vec2(0.0, 0.0), // Anchor rotation
        vec2(0.5, 0.5), // Shift image from center
        scale, angle,
        true, // repeat
        true, 2.0 // Undo gamma correction, gamma value
    );

    col.a = 3.0 - length(gluv_all);
    return col;
}