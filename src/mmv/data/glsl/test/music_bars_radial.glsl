

// ===============================================================================

#pragma map name music_bars_radial

#pragma include mmv_specification once;
#pragma map fft=pipeline_texture;;{MMV_FFTSIZE}x1;
#pragma map logo=image;{LOGO_IMAGE};1000x1000

// A is proportional to B
// C is proportional to what?
// what = b*c / a for a \neq 0
float proportion(float a, float b, float c) {
    return (b * c) / a;
}

float atan2(in float y, in float x)
{
    #pragma include math_constants multiple
    bool s = (abs(x) > abs(y));
    return mix(PI/2.0 - atan(x,y), atan(y,x), s);
}

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple

    vec4 col = vec4(0.0);

    // Angle relative to the center
    float angle_offset = (PI / 4) * sin(progressive_amplitude/8.0)*0.16;
    float speed = 0.3;
    float amplitude = 0.004 * smooth_audio_amplitude;
    vec2 offset = vec2(sin(5.0 * mmv_time * speed) * amplitude, cos(8.0 * mmv_time * speed) * amplitude);
    vec2 gluv_offsetted = gluv - offset;
    vec2 get_visualizer_angle = gluv_offsetted * get_rotation_mat2((PI / 2.0) + angle_offset);
    float angle = atan(get_visualizer_angle.y, get_visualizer_angle.x) * sign(get_visualizer_angle.y);

    // atan symmetries
    if (get_visualizer_angle.y < 0) {
        angle += PI;
    }

    // Which index
    int which = int({MMV_FFTSIZE} * proportion(2 * PI, 1, angle));
    float fft_val = texelFetch(fft, ivec2(which, 0), 0).r;

    float size = (0.16) + smooth_audio_amplitude2 * 0.009;
    float bar_size = 0.4;

    if (length(gluv_offsetted) < (size + (fft_val/5024.0) * bar_size)) {
        col = vec4(vec3(
            1.0 - fft_val / 5000,
            1.0,
            1.0
        ), 1.0);
    }

    vec4 logo_pixel = mmv_blit_image(
        col, logo,
        logo_resolution,
        gluv_offsetted,
        vec2(0.0, 0.0), // anchor
        vec2(0.5, 0.5), // shift
        size * 2.0,  //scale
            sin(mmv_time*2.3 + progressive_amplitude/8.0) / 8.0
            + sin(mmv_time*2.3 + progressive_amplitude/5.0) / 8.0, //angle
        false
    );
    col = mix(col, logo_pixel, logo_pixel.a);

    // if (stuv.y < sqrt(fft_val/9000)) {
    //     col = vec4(shadertoy_uv.x, stuv.y * fft_val/20.0, 1.0 - standard_deviations[2] - stuv.y*4.0, 1.0);
    // } else {
    //     col = vec4(vec3(smooth_audio_amplitude/4.0), 0.0);
    // }

    fragColor = col;
}
