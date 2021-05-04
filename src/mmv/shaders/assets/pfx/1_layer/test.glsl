
vec4 mainImage() {
    vec4 col = vec4(1.0);
    col = texture(layer0, shadertoy_uv);
    col.r = shadertoy_uv.x;
    return col;
}