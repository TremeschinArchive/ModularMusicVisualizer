// ===============================================================================
//#shadermaker includes
//#shadermaker mappings
//#shadermaker functions
// ===============================================================================

//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_rms_0_20;

vec4 rain_layer(vec2 uv, float amount) {
    //#mmv {"type": "include", "value": "math_constants", "mode": "multiple"}

    // Apply scaling, get grid uv and id. We get mod of floor since 500 repetitions
    // is enough and mmv_N21 will have some troubles with big numbers
    vec2 grid = fract(uv);
    vec2 id = mod(floor(uv), 500);

    // Default return empty
    vec4 col = vec4(0.0);
    float grid_noise = mmv_N21(id);

    // If we're below some amount
    if (grid_noise < amount) {
        col = vec4(1.0);
        col.a = (pow(sin(grid.x * PI), 80.0) * sin(grid.y * PI) - 0.4) * ((1.0 / amount) * grid_noise);
        if (col.a < 0.0) { col.a = 0; }
    }

    return col;
}

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);
    int nlayers = 9;

    for (float i = 0; i < 1; i += 1.0 / nlayers) {

        vec2 luv = stuv_all;
        luv *= (30.0 + i*20.0);

        // Rotation
        luv *= get_rotation_mat2(radians(-30 + 15 * i + sin(mmv_time*i) / 2.0));

        // Offset
        vec2 offset = vec2(sin(mmv_time * i * 5.0), cos(mmv_time * (1.0 - i) * 8.0)) / 80.0;
        luv += offset + vec2(0.0, mmv_time * (10.0 + 30.0 * i));

        col.a *= 0.4 + 0.6 * i;

        // Add rain layer
        col += rain_layer(luv, 0.01);
    }

    fragColor = col;
}

