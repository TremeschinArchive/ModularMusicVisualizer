
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);

    // User stuff
    float intensity = 0.5;

    // Shortcuts
    float w = mResolution[0];
    float h = mResolution[1];

    // Offsets
    vec2 red_offset   = intensity * vec2(15*sin((mTime)) / w, 25*cos(1.35135*(mTime)) / h);
    vec2 green_offset = intensity * vec2(20*cos(1.2315*(mTime)) / w, 20*sin(3.2315*(mTime)) / h);
    vec2 blue_offset  = intensity * vec2(10*cos(5.34235*(mTime)) / w, 13*cos(1.35634*(mTime)) / h);

    // // Calculate it

    // Raw, without chromatic aberration
    vec4 base_layer = texture(layer0, ShaderToyUV);

    // Define color and use layer's alpha
    col = vec4(
        texture(layer0, ShaderToyUV + red_offset  ).r,
        texture(layer0, ShaderToyUV + green_offset).g,
        texture(layer0, ShaderToyUV + blue_offset ).b,
        base_layer.a
    );

    return col;
}
