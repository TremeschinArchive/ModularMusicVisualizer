
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_audio_rms_0_33;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    //#mmv {"type": "include", "value": "math_constants", "mode": "multiple"}

    // Start with empty color (so it's fully transparent everywhere)
    vec4 col = vec4(0.0);

    vec2 uv = stuv_all;
    uv.x /= resratio;

    float fft_val_l = texelFetch(mmv_audio_fft_linear, ivec2(int(uv.x * mmv_audio_fft_linear_width) / 2, 0), 0).r;
    float fft_val_r = texelFetch(mmv_audio_fft_linear, ivec2(int(mmv_audio_fft_linear_width / 2) + int(uv.x * mmv_audio_fft_linear_width) / 2, 0), 0).r;


    if (uv.y < pow(fft_val_l / 180, 0.8)) {
        col += vec4(fft_val_l/40, 0.0, 0.0, 0.15);
    }

    if (uv.y < pow(fft_val_r / 180, 0.8)) {
        col += vec4(0.0, 0.0, fft_val_l/40, 0.15);
    }

    // Return color
    fragColor = col;
}
