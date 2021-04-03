// ===============================================================================
//#shadermaker includes
//#shadermaker mappings
//#shadermaker functions
// ===============================================================================

// EXPECTS: sampler2D named "layer" on the texture to be applied

// ===============================================================================

uniform vec3 mmv_progressive_rms_0_05;
uniform vec3 mmv_rms_0_15;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // User stuff
    float intensity = (mmv_rms_0_15[2] / 2.5) / mmv_zoom;
    float add = mmv_progressive_rms_0_05[2] / 18.0;

    // Shortcuts
    float w = mmv_resolution[0];
    float h = mmv_resolution[1];

    // Offsets
    vec2 red_offset   = intensity * vec2(15*sin((mmv_time + add)) / w, 25*cos(1.35135*(mmv_time + add)) / h);
    vec2 green_offset = intensity * vec2(20*cos(1.2315*(mmv_time + add)) / w, 20*sin(3.2315*(mmv_time + add)) / h);
    vec2 blue_offset  = intensity * vec2(10*cos(5.34235*(mmv_time + add)) / w, 13*cos(1.35634*(mmv_time + add)) / h);

    // // Calculate it

    // Raw, without chromatic aberration
    vec4 base_layer = texture(layer, shadertoy_uv);

    // Define color and use layer's alpha
    col = vec4(
        texture(layer, shadertoy_uv + red_offset  ).r,
        texture(layer, shadertoy_uv + green_offset).g,
        texture(layer, shadertoy_uv + blue_offset  ).b,
        base_layer.a
    );

    // col = texture(layer, shadertoy_uv + red_offset);
    fragColor = col;
}

