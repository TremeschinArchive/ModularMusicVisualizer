
// ===============================================================================

#pragma map name fourier_glsl_test

#pragma map layer1=shader;{LAYER1};{WIDTH}x{HEIGHT}
#pragma map layer2=shader;{LAYER2PFX};{WIDTH}x{HEIGHT}
#pragma map layer_particles=shader;{LAYER_PARTICLES};{WIDTH}x{HEIGHT}

uniform float smooth_audio_amplitude;
uniform float progressive_amplitude;

vec4 bloom(sampler2D tex, vec2 uv, vec2 resolution, int size, bool alpha_zero_dont_calculate) {
    vec4 original = texture(tex, uv);

    if (size == 0) {
        return original;
    }

    if ((original.a == 1.0) && (alpha_zero_dont_calculate)) {
        return original;
    }

    vec4 blur = vec4(0.0);
    ivec2 get_image = ivec2(uv * resolution);

    if (
        texelFetch(tex, get_image + ivec2(-size,  0), 0).a == 0 &&
        texelFetch(tex, get_image + ivec2( size,  0), 0).a == 0 &&
        texelFetch(tex, get_image + ivec2( 0, -size), 0).a == 0 &&
        texelFetch(tex, get_image + ivec2( 0,  size), 0).a == 0
    ) {
        return original;
    }

    for (int x = -size; x < size; x++) {
        for (int y = -size; y < size; y++) {
            float d = (size * sqrt(2));
            blur += texelFetch(tex, get_image + ivec2(x, y), 0);
        }
    }

    blur /= size * size;

    return blur / 3.0;
}

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple

    float scale = (atan(mmv_time * 2.0) / PI) * 2;
    vec2 shadertoy_uv_scaled = shadertoy_uv;
    vec2 opengl_uv_scaled = opengl_uv;

    if(scale < 0.99) {
        stuv *= scale;
        gluv *= scale;
        
        shadertoy_uv_scaled *= scale;
        shadertoy_uv_scaled += (vec2(0.5, 0.5) * (1.0 - scale));
        opengl_uv_scaled *= scale;
    }

    vec4 col = vec4(0.0);
    vec4 layer = vec4(0.0);
    
    bool chromatic_aberration = true;
    bool do_bloom = true;
    int bloom_amount = 0;

    // // Layer 1

    chromatic_aberration = true;
    do_bloom = false;
    bloom_amount = int(smooth_audio_amplitude/6.0);

    if (chromatic_aberration) {
        float amount = ((1 / mmv_resolution.x) * smooth_audio_amplitude) * 0.9;
        float pa = progressive_amplitude/2.0;
        vec2 get_r = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude + pa), cos(smooth_audio_amplitude + pa)) * amount;
        vec2 get_g = shadertoy_uv_scaled + vec2(cos(smooth_audio_amplitude/3.3243 + pa), sin(smooth_audio_amplitude*1.2312 + pa)) * amount;
        vec2 get_b = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude/2.0  + pa) * amount);
        vec2 get_a = shadertoy_uv_scaled;

        if (do_bloom){
            vec4 br = bloom(layer1, get_r, layer1_resolution, bloom_amount, false);
            vec4 bg = bloom(layer1, get_g, layer1_resolution, bloom_amount, false);
            vec4 bb = bloom(layer1, get_b, layer1_resolution, bloom_amount, false);
            layer = vec4(
                br.r, bg.g, bb.b,
                (br.a + bg.a + bb.a) / 3.0
            );
        } else {
            layer = vec4(
                texture(layer1, get_r).r,
                texture(layer1, get_g).g,
                texture(layer1, get_b).b,
                texture(layer1, get_a).a
            );
        }
    } else {
        layer = texture(layer1, shadertoy_uv_scaled);
    }
    col = mix(layer, col, 1.0 - layer.a);
    
    if (do_bloom && ! chromatic_aberration) {
        layer = bloom(layer1, shadertoy_uv_scaled, layer1_resolution, bloom_amount, false);
    }

    // // Layer 2

    layer = texture(layer_particles, shadertoy_uv_scaled);
    col = mix(layer, col, 1.0 - layer.a);

    // // Layer 3

    chromatic_aberration = true;
    do_bloom = true;
    bloom_amount = 8;

    if (chromatic_aberration) {
        float amount = ((1 / mmv_resolution.x) * smooth_audio_amplitude) * 0.9;
        float pa = progressive_amplitude/2.0;
        vec2 get_r = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude + pa), cos(smooth_audio_amplitude + pa)) * amount;
        vec2 get_g = shadertoy_uv_scaled + vec2(cos(smooth_audio_amplitude/3.3243 + pa), sin(smooth_audio_amplitude*1.2312 + pa)) * amount;
        vec2 get_b = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude/2.0  + pa) * amount);
        vec2 get_a = shadertoy_uv_scaled;

        if (do_bloom) {
            vec4 br = bloom(layer2, get_r, layer2_resolution, bloom_amount, true);
            vec4 bg = bloom(layer2, get_g, layer2_resolution, bloom_amount, true);
            vec4 bb = bloom(layer2, get_b, layer2_resolution, bloom_amount, true);
            float tr = 0.96;
            layer = vec4(
                br.r, bg.g, bb.b,
                ((br.a + bg.a + bb.a) * tr) / 3.0
            );
        } else {
            layer = vec4(
                texture(layer2, get_r).r,
                texture(layer2, get_g).g,
                texture(layer2, get_b).b,
                texture(layer2, get_a).a
            );
        }
    } else {
        layer = texture(layer2, shadertoy_uv_scaled);
    }

    col = mix(layer, col, 1.0 - layer.a);

    if (do_bloom && ! chromatic_aberration) {
        layer = bloom(layer2, shadertoy_uv_scaled, layer2_resolution, bloom_amount, true);
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
