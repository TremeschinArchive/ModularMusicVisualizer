
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(1.0);
    col = texture(layer0, shadertoy_uv);
    col.r = shadertoy_uv.x;
    return col;
}