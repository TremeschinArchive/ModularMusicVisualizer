
// ===============================================================================

#pragma map name fourier_layer_background

#pragma include mmv_specification once
#pragma map background=image;{BACKGROUND};1920x1080

uniform float smooth_audio_amplitude;
uniform vec3 standard_deviations;
uniform vec3 average_amplitudes;
uniform float progressive_amplitude;

void main() {
    #pragma include coordinates_normalization multiple
    
    vec4 col = vec4(0.0);

    float shake_speed_audio = 1/20;
    float shake_speed_time = 1.0 / 4.0;
    float shake_amplitude = 3 + 7 * smooth_audio_amplitude;
    vec2 shake = vec2(
        sin(((mmv_time * shake_speed_time) + (smooth_audio_amplitude * shake_speed_audio)) * 5.0),
        cos(((mmv_time * shake_speed_time) + (smooth_audio_amplitude * shake_speed_audio)) * 8.0)
    ) * shake_amplitude * (1 / mmv_resolution.x);

    col = mmv_blit_image(
        col, background,
        background_resolution,
        (gluv / 2.0) + shake,
        vec2(0.0, 0.0), // anchor
        vec2(0.5, 0.5), // shift
        1.0 + smooth_audio_amplitude/60.5,  //scale
        sin(progressive_amplitude)/300.0, //angle
        true
    );

    fragColor = col;
}
