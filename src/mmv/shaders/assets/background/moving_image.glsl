
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_rms_0_20;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // Displacement stuff for organic movement
    vec2 low_freq_shake = vec2(cos(mmv_time*5.0/1.5), sin(mmv_time*8.0/1.5)) / 180.0;
    vec2 high_freq_shake = vec2(cos(mmv_time*10.0/1.3), sin(mmv_time*16.0/1.3)) / 300.0;
    vec2 offset = vec2(sin(mmv_time/7.135135), cos(mmv_time/4.523894)) / 20.0;

    // Scale and angle
    float scale = 2.2 + mmv_rms_0_20[2] * 0.2;
    float angle = sin(mmv_time)/80.0;

    // Linear transformation on where to get the texture of the image
    vec2 get_image_uv = gluv_all;
    get_image_uv += low_freq_shake + high_freq_shake + offset;

    // Blit image
    col += mmv_blit_image(
        col, background, // NOTE: We expect a "background" sampler2D mapped!
        background_resolution, // res
        get_image_uv, // uv
        vec2(0.0, 0.0), // Anchor rotation
        vec2(0.5, 0.5), // Shift image from center
        scale, angle,
        true, // repeat
        true, 2.0 // Undo gamma correction, gamma value
    );

    fragColor = col;
}

