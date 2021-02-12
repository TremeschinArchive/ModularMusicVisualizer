
// ===============================================================================

#pragma map name fourier_layer_background

#pragma include mmv_specification once

#pragma map background=image:{BACKGROUND}:1920x1080

uniform float smooth_audio_amplitude;
uniform vec3 standard_deviations;
uniform vec3 average_amplitudes;

void main() {
    #pragma include coordinates_normalization multiple
    
    vec4 col = vec4(0.0);

    col = mmv_blit_image(
        col, background,
        background_resolution,
        gluv / 2.0,
        vec2(0.0, 0.0), // anchor
        vec2(0.5, 0.5), // shift
        1.0 + smooth_audio_amplitude/6.5,  //scale
        sin(standard_deviations.b * 500.0)/600.0, //angle
        true
    );

    fragColor = col;
}
