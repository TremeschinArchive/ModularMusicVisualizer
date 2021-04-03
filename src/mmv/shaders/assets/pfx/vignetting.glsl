// ===============================================================================
//#shadermaker includes
//#shadermaker mappings
//#shadermaker functions
// ===============================================================================

uniform vec3 mmv_rms_0_15;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    vec2 uv = shadertoy_uv;

    // "Asymptote" in the edges
    uv *= 1.0 - uv.yx;
    
    // Raw ammount of vignetting
    float vignetting = uv.x * uv.y * 30.0;
    vignetting = pow(vignetting, 0.3 + mmv_rms_0_15[2] / 6.0);

    // Assign to alpha channel so this is alpha composided to black
    col.a = 1.0 - vignetting;

    fragColor = col;
}

