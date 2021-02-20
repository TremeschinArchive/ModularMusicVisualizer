
// ===============================================================================

#pragma map name fourier_glsl_test

#pragma include mmv_specification once
#pragma map fft=pipeline_texture;;{MMV_FFTSIZE}x1

void main() {
    #pragma include coordinates_normalization multiple;

    vec4 col = vec4(0.0);

    // Which index
    int which = int({MMV_FFTSIZE} * shadertoy_uv.x);
    float fft_val = texelFetch(fft, ivec2(which, 0), 0).r;

    stuv.y -= 0.0;
        
    if (stuv.y < sqrt(fft_val/9000)) {
        col = vec4(shadertoy_uv.x, stuv.y * fft_val/20.0, 1.0 - standard_deviations[2] - stuv.y*4.0, 1.0);
    } else {
        col = vec4(smooth_audio_amplitude/4.0);
    }

    fragColor = col;
}
