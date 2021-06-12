
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);
    vec2 uv = shadertoy_uv;

    // Top and bottom bar for cinematics
    float bar = 0.03;
    uv.y *= 1 + bar;
    uv -= vec2(0, bar/2);
    vec2 uv_bar = uv;

    // "Asymptote" in the edges
    uv *= 1.0 - uv.yx;

    // Raw ammount of vignetting
    float vignetting = uv.x * uv.y * 90.0;
    vignetting = pow(vignetting, 0.3);

    if (uv_bar.y < 0 || uv_bar.y > 1) {
        vignetting = 0.03;
    }

    // Assign to alpha channel so this is alpha composided to black
    col.a = 1.0 - vignetting;

    return col;
}

