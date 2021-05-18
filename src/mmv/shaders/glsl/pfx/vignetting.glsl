
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);

    vec2 uv = shadertoy_uv;

    // "Asymptote" in the edges
    uv *= 1.0 - uv.yx;
    
    // Raw ammount of vignetting
    float vignetting = uv.x * uv.y * 30.0;
    vignetting = pow(vignetting, 0.3);

    // Assign to alpha channel so this is alpha composided to black
    col.a = 1.0 - vignetting;

    return col;
}

