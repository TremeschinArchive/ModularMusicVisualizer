// ===============================================================================
//                                 GPL v3 License                                
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
// See LICENSE.md, this is compact header for not cluttering final shaders
// ===============================================================================

#pragma include mmv_specification;
#pragma map fft=pipeline_texture::{MMV_FFTSIZE}x1;

uniform float smooth_audio_amplitude;
uniform vec3 standard_deviations;
uniform vec3 average_amplitudes;

void main() {
    #pragma include coordinates_normalization;

    vec4 col = vec4(0.0);

    // Which index
    int which = int({MMV_FFTSIZE} * shadertoy_uv.x);
    float fft_val = texelFetch(fft, ivec2(which, 0), 0).r;
        
    if (stuv.y * 90.0 < fft_val) {
        col = vec4(0.8, stuv.y * fft_val/20.0, 1.0 - standard_deviations[2] - stuv.y*4.0, 1.0);
    } else {
        col = vec4(smooth_audio_amplitude/4.0);
    }

    fragColor = col;
}
