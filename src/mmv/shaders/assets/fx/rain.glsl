
vec4 rain_layer(vec2 uv, float amount) {

    // Apply scaling, get grid uv and id. We get mod of floor since 500 repetitions
    // is enough and mN21 will have some troubles with big numbers
    vec2 grid = fract(uv);
    vec2 id = mod(floor(uv), 500);

    // Default return empty
    vec4 col = vec4(0.0);
    float grid_noise = mN21(id);

    // If we're below some amount
    if (grid_noise < amount) {
        col = vec4(1.0);
        col.a = (pow(sin(grid.x * PI), 80.0) * sin(grid.y * PI) - 0.4)
            * ((1.0 / amount) * grid_noise); // Random value
        if (col.a < 0.0) { col.a = 0; }
    }

    return col;
}

vec4 mainImage() {
    vec4 col = vec4(0.0);
    int nlayers = 8;
    vec2 gluv_all = mGetGLUVParallax(1.5);

    for (float i = 0; i < 1; i += 1.0 / nlayers) {

        vec2 luv = gluv_all;
        luv *= (10.0 + i*20.0);

        // Rotation
    
        // Offset
        vec2 offset = vec2(100*i, 200*i) + vec2(sin(mTime * i * 5.0), cos(mTime * (1.0 - i) * 8.0)) / 80.0;
        luv *= mRotation2D(radians(-30 + 15 * i + sin(mTime*i) / 2.0));
        luv += offset + vec2(0.0, mTime * (10.0 + 30.0 * i));

        col.a *= 0.4 + 0.6 * i;

        // Add rain layer
        col += rain_layer(luv, 0.01);
    }

    return col;
}

