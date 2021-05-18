
vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(1.0);
    vec2 stuv_all = mGetSTUVAll();
    vec2 gluv_all = mGetGLUVParallax(0.7);

    // Backgound color
    col.rgb = vec3(0.0 / 256, 38.0 / 256, 130.0 / 256);

    // Displacement stuff for organic movement
    vec2 low_freq_shake = vec2(cos(mTime*5.0/1.5), sin(mTime*8.0/1.5)) / 30.0;
    vec2 high_freq_shake = vec2(cos(mTime*10.0/1.3), sin(mTime*16.0/1.3)) / 90.0;
    vec2 offset = vec2(sin(mTime/7.135135), cos(mTime/4.523894)) / 20.0;

    // Scale and angle
    float scale = 3.2 + 0.2;
    float angle = sin(mTime)/30.0;

    // // UV coordinates for getting the grid

    vec2 uv = (gluv_all) * scale;
    float multiplier = 0.5 * log(length(uv) + 20);
    uv += vec2(0.5) / multiplier;

    // Add stuf, apply scaling, offset and rotate
    uv += low_freq_shake + high_freq_shake + offset;
    uv *= m2DRotation2D(angle);

    // Interesting one
    // uv *= 1.41 - log(length(opengl_uv));
    uv *= multiplier;

    // // Grids uv with fract and id with floor
    vec2 grid = fract(uv);
    vec2 grid_id = floor(uv);

    // Make center of grid (0, 0)
    grid += vec2(0.5);

    // // Lines

    // Config
    vec4 major_line = vec4(1.0);
    vec4 minor_line = vec4(vec3(1.0), 0.3);
    float major_line_size = 0.03;
    float minor_line_size = 0.015;
    int major_line_every = 5;

    // Abs distance to the 0.5 center coordinate
    float x = abs(grid.x - 0.5);
    float y = abs(grid.y - 0.5);

    // Calculate major line with smoothstep
    float major_h_line = 1.0 - smoothstep(0.5 + major_line_size, 0.5, y) * smoothstep(0.5 - major_line_size, 0.5, y);
    float major_v_line = 1.0 - smoothstep(0.5 + major_line_size, 0.5, x) * smoothstep(0.5 - major_line_size, 0.5, x);

    // Calculate minor line with smoothstep
    float minor_h_line = 1.0 - smoothstep(0.5 + minor_line_size, 0.5, y) * smoothstep(0.5 - minor_line_size, 0.5, y);
    float minor_v_line = 1.0 - smoothstep(0.5 + minor_line_size, 0.5, x) * smoothstep(0.5 - minor_line_size, 0.5, x);

    // If we're major or minor
    bool is_x_major = mod(grid_id.x, major_line_every) == 0;
    bool is_y_major = mod(grid_id.y, major_line_every) == 0;

    // Put the color based on grid minor or major, finicky values also doesn't fully work
    // because we write on top instead of drawing the grids and alpha compositing
    if (is_x_major && is_y_major) {
        col = mix(major_line, col, major_v_line);
        col = mix(major_line, col, major_h_line);
    } else if (is_x_major) {
        col = mix(major_line, col, major_v_line);
        col = mix(minor_line, col, minor_h_line);
    } else if (is_y_major) {
        col = mix(minor_line, col, minor_v_line);
        col = mix(major_line, col, major_h_line);
    } else {
        col = mix(minor_line, col, minor_v_line);
        col = mix(minor_line, col, minor_h_line);
    }

    // Saturate the edges just for some more fun
    col = mSaturate(col, 1.0 + pow(length(opengl_uv), 3.0) );

    return col;
}