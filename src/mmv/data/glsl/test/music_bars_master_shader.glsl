
// ===============================================================================

#pragma map name music_bars_master_shader
#pragma map background_shader=dynshader;{BACKGROUND_SHADER}
#pragma map music_bars_pfx=dynshader;{MUSIC_BARS_SHADER_PFX}
#pragma map particles_layer=dynshader;{PARTICLES_SHADER}

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

vec4 acomposite(vec4 new, vec4 old) {
    return mix(old, new, new.a);

    // float final_alpha = new.a + old.a * (1 - new.a);
    // return vec4(((new.rgb * new.a) + (old.rgb * old.a * (1 - new.a))) / final_alpha, final_alpha);
}

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple

    vec2 shadertoy_uv_scaled = shadertoy_uv;
    vec2 opengl_uv_scaled = opengl_uv;

    float scale = (atan(mmv_time * 2.0) / PI) * 2;
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
    float chromatic_aberration_amount = 0.0;
    bool do_bloom = true;
    int bloom_amount = 0;

    // // Layer 1

    chromatic_aberration = false;
    do_bloom = false;
    bloom_amount = int(smooth_audio_amplitude/6.0);
    chromatic_aberration_amount = ((1 / mmv_resolution.x) * smooth_audio_amplitude) * 0.05;

    if (chromatic_aberration) {
        float pa = progressive_amplitude/2.0;
        vec2 get_r = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude + pa), cos(smooth_audio_amplitude + pa)) * chromatic_aberration_amount;
        vec2 get_g = shadertoy_uv_scaled + vec2(cos(smooth_audio_amplitude/3.3243 + pa), sin(smooth_audio_amplitude*1.2312 + pa)) * chromatic_aberration_amount;
        vec2 get_b = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude/2.0  + pa) * chromatic_aberration_amount);
        vec2 get_a = shadertoy_uv_scaled;

        get_r = clamp(get_r, 0.0, 1.0);
        get_g = clamp(get_g, 0.0, 1.0);
        get_b = clamp(get_b, 0.0, 1.0);

        if (do_bloom){
            vec4 br = bloom(background_shader, get_r, mmv_resolution, bloom_amount, false);
            vec4 bg = bloom(background_shader, get_g, mmv_resolution, bloom_amount, false);
            vec4 bb = bloom(background_shader, get_b, mmv_resolution, bloom_amount, false);
            layer = vec4(
                br.r, bg.g, bb.b,
                (br.a + bg.a + bb.a) / 3.0
            );
        } else {
            layer = vec4(
                texture(background_shader, get_r).r,
                texture(background_shader, get_g).g,
                texture(background_shader, get_b).b,
                texture(background_shader, get_a).a
            );
        }
    } else {
        layer = texture(background_shader, shadertoy_uv_scaled);
    }
    col = acomposite(layer, col);
    
    if (do_bloom && ! chromatic_aberration) {
        layer = bloom(background_shader, shadertoy_uv_scaled, background_shader_resolution, bloom_amount, false);
    }

    // // Layer 2

    layer = texture(particles_layer, shadertoy_uv_scaled);
    col = acomposite(layer, col);

    // // Layer 3

    chromatic_aberration = true;
    do_bloom = false;
    bloom_amount = 3;
    chromatic_aberration_amount = ((1 / mmv_resolution.x) * smooth_audio_amplitude) * 0.14;

    if (chromatic_aberration) {
        float pa = progressive_amplitude/2.0;
        vec2 get_r = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude + pa), cos(smooth_audio_amplitude + pa)) * chromatic_aberration_amount;
        vec2 get_g = shadertoy_uv_scaled + vec2(cos(smooth_audio_amplitude/3.3243 + pa), sin(smooth_audio_amplitude*1.2312 + pa)) * chromatic_aberration_amount;
        vec2 get_b = shadertoy_uv_scaled + vec2(sin(smooth_audio_amplitude/2.0  + pa) * chromatic_aberration_amount);
        vec2 get_a = shadertoy_uv_scaled;

        get_r = clamp(get_r, 0.0, 1.0);
        get_g = clamp(get_g, 0.0, 1.0);
        get_b = clamp(get_b, 0.0, 1.0);

        if (do_bloom) {
            vec4 br = bloom(music_bars_pfx, get_r, mmv_resolution, bloom_amount, true);
            vec4 bg = bloom(music_bars_pfx, get_g, mmv_resolution, bloom_amount, true);
            vec4 bb = bloom(music_bars_pfx, get_b, mmv_resolution, bloom_amount, true);
            float tr = 0.985 - (0.01 * clamp(smooth_audio_amplitude, 0.0, 6.0));
            layer = vec4(
                br.r, bg.g, bb.b,
                ((br.a + bg.a + bb.a) * tr) / 3.0
            );
        } else {
            layer = vec4(
                texture(music_bars_pfx, get_r).r,
                texture(music_bars_pfx, get_g).g,
                texture(music_bars_pfx, get_b).b,
                texture(music_bars_pfx, get_a).a
            );
        }
    } else {
        layer = texture(music_bars_pfx, shadertoy_uv_scaled);
    }
    col = acomposite(layer, col);;

    if (do_bloom && ! chromatic_aberration) {
        layer = bloom(music_bars_pfx, shadertoy_uv_scaled, music_bars_pfx_resolution, bloom_amount, true);
    }

    vec4 vignetting = vec4(vec3(0.0), smooth_audio_amplitude * length(gluv) / 65.0);
    vec4 gray_scale = vec4(vec3((col.r + col.g + col.b) / 3.0), 1.0);
    col = mix(vignetting, col, 1.0 - vignetting.a);
    col = mix(
        gray_scale, col,
        1.0 - vignetting.a
    );

    fragColor = col;
}

