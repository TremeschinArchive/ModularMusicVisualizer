
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);
    
    int kernel = 5;

    for (int x = -kernel; x < kernel; x++) {
        for (int y = -kernel; y < kernel; y++) {
            col += texture(layer0, shadertoy_uv + (vec2(x, y) / mResolution));
        }
    }

    col /= kernel*kernel;

    return col;
}