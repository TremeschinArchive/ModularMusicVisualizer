
// ===============================================================================

#pragma map name fourier_glsl_test

#pragma map layer1=shader;{LAYER1};{WIDTH}x{HEIGHT}
#pragma map layer2=shader;{LAYER2PFX};{WIDTH}x{HEIGHT}

uniform float smooth_audio_amplitude;
uniform float progressive_amplitude;

void main() {
    #pragma include coordinates_normalization multiple

    vec4 col = vec4(0.0);
    vec4 layer = vec4(0.0);

    layer = texture(layer1, shadertoy_uv);
    col = mix(layer, col, 1.0 - layer.a);

    bool chromatic_aberration = true;

    if (chromatic_aberration) {
        float amount = ((1 / mmv_resolution.x) * smooth_audio_amplitude) * 0.7;
        float pa = progressive_amplitude/2.0;
        vec2 get_r = shadertoy_uv + vec2(sin(smooth_audio_amplitude + pa), cos(smooth_audio_amplitude + pa)) * amount;
        vec2 get_g = shadertoy_uv + vec2(cos(smooth_audio_amplitude/3.3243 + pa), sin(smooth_audio_amplitude*1.2312 + pa)) * amount;
        vec2 get_b = shadertoy_uv + vec2(sin(smooth_audio_amplitude/2.0  + pa) * amount);
        vec2 get_a = shadertoy_uv;
        
        layer = vec4(
            texture(layer2, get_r).r,
            texture(layer2, get_g).g,
            texture(layer2, get_b).b,
            texture(layer2, get_a).a
        );

        col = mix(layer, col, 1.0 - layer.a);

    } else {
        layer = texture(layer2, shadertoy_uv);
        col = mix(layer, col, 1.0 - layer.a);
    }

    vec4 vignetting = vec4(vec3(0.0), smooth_audio_amplitude * length(gluv) / 30.0);
    vec4 gray_scale = vec4(vec3((col.r + col.g + col.b) / 3.0), 1.0);
    col = mix(vignetting, col, 1.0 - vignetting.a);
    col = mix(
        gray_scale, col,
        1.0 - vignetting.a
    );

    fragColor = col;
}

