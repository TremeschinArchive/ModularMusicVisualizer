
// ===============================================================================

#pragma map name fourier_glsl_test

#pragma map layer1=shader;{LAYER1};{WIDTH}x{HEIGHT}
#pragma map layer2=shader;{LAYER2PFX};{WIDTH}x{HEIGHT}

uniform float smooth_audio_amplitude;

void main() {
    #pragma include coordinates_normalization multiple

    vec4 col = vec4(0.0);
    vec4 layer = vec4(0.0);

    layer = texture(layer1, shadertoy_uv);
    col = mix(layer, col, 1.0 - layer.a);

    layer = texture(layer2, shadertoy_uv);
    col = mix(layer, col, 1.0 - layer.a);

    vec4 vignetting = vec4(vec3(0.0), smooth_audio_amplitude * length(gluv) / 15.0);
    vec4 gray_scale = vec4(vec3((col.r + col.g + col.b) / 3.0), 1.0);
    col = mix(vignetting, col, 1.0 - vignetting.a);
    col = mix(
        gray_scale, col,
        1.0 - vignetting.a
    );

    fragColor = col;
}

