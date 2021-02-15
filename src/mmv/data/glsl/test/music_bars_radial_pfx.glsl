
// ===============================================================================

#pragma map name music_bars_radial_pfx

#pragma map layer2=shader;{MUSIC_BARS_SHADER};{WIDTH}x{HEIGHT}

#pragma include mmv_specification once

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple
    
    vec4 col = vec4(0.0);

    // Original pixel
    vec4 layer_1_raw = texture(layer2, shadertoy_uv);    

    if (layer_1_raw.a >= 0.9) {
        fragColor = layer_1_raw;
        // fragColor = layer_1_raw;
        return;
    }

    float bluramount = 10.0;
    vec2 radius = bluramount / mmv_resolution.xy;
    float directions = 10.0;
    float steps = bluramount;

    // Keep summing
    vec4 sum_pixels = texture(layer2, shadertoy_uv);

    // The radians we walk
    for(float rad = 0.0; rad < PI; rad += (2.0 * PI) / directions) {
        // The growth from the center we walk
        for(float dr = 1.0 / steps; dr <= 1.0; dr += 1.0 / steps) {
            sum_pixels += texture(layer2, shadertoy_uv + (vec2(cos(rad), sin(rad)) * radius * dr));		
        }
    }

    sum_pixels /= steps * directions;

    fragColor = sum_pixels;
}