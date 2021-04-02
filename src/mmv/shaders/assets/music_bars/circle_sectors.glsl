// ===============================================================================
//#shadermaker includes
//#shadermaker mappings
//#shadermaker functions
// ===============================================================================

//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_rms_0_33;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    //#mmv {"type": "include", "value": "math_constants", "mode": "multiple"}

    vec4 col = vec4(0.0);

    // Angle relative to the center
    float angle_offset = (PI / 4) * sin(mmv_progressive_rms[2] / 16.0)*0.16;
    float speed = 0.3;
    float amplitude = 0.102 * mmv_rms_0_33[2];
    vec2 offset = vec2(sin(5.0 * mmv_time * speed) * amplitude, cos(8.0 * mmv_time * speed) * amplitude);
    vec2 gluv_offsetted = gluv_all - offset;
    vec2 get_visualizer_angle = gluv_offsetted * get_rotation_mat2(-(PI / 2.0) + angle_offset);
    float angle = atan(get_visualizer_angle.y, get_visualizer_angle.x) * sign(get_visualizer_angle.y);

    // // Which index

    // Circle sectors
    bool smooth_bars = true;
    float which = 0.0;
    float fft_val = 0.0;

    if (smooth_bars) {
        which = mmv_proportion(2 * PI, 1, angle);
        fft_val = texture(mmv_fft, vec2(which, 0), 0).r;
    } else {
        which = int({MMV_FFTSIZE} * mmv_proportion(2 * PI, 1, angle));
        fft_val = texelFetch(mmv_fft, ivec2(which, 0), 0).r;
    }

    // // 
    bool angelic = true;
    float size = (0.13) + mmv_rms_0_33[2] * 0.133;
    float bar_size = 0.4;
    float logo_relative_to_bar_ratio = 1.0 - (0.05 * smoothstep(mmv_rms_0_33[2], 0.0, 5.0));

    if (length(gluv_offsetted) < (size + (fft_val/50.0) * bar_size)) {
        col = vec4(vec3(
            1.0 - fft_val / 50, 1.0, 1.0
        ), 1.0);
    } else {
        if (angelic) {
            col += (size + (fft_val/50.0) * bar_size) / (1.5 * length(gluv_offsetted));
        }
    }

    vec4 logo_pixel = mmv_blit_image(
        col, logo,
        logo_resolution,
        gluv_offsetted,
        vec2(0.0, 0.0), // anchor
        vec2(0.5, 0.5), // shift
        size * 2.0 * logo_relative_to_bar_ratio,  //scale
            sin(mmv_time*2.3 + mmv_progressive_rms[2]/8.0) / 8.0
            + sin(mmv_time*2.3 + mmv_progressive_rms[2]/5.0) / 8.0, //angle
        false, // repeat
        true, 2.0 // Undo gamma, Gamma
    );
    col = mix(col, logo_pixel, logo_pixel.a);

    // if (stuv.y < sqrt(fft_val/9000)) {
    //     col = vec4(shadertoy_uv.x, stuv.y * fft_val/20.0, 1.0 - standard_deviations[2] - stuv.y*4.0, 1.0);
    // } else {
    //     col = vec4(vec3(mmv_rms_0_33[2]/4.0), 0.0);
    // }

    fragColor = col;
}
