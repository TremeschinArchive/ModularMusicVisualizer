// ===============================================================================

// Heavily inspired, implementation """copied""" (I commented, named the vars on
// my own, implemented MMV code on top of this nice shader) from our Shader God
// The Art of Code: https://www.youtube.com/watch?v=3CycKKJiwis, Thank you very much
// for teaching and showcasing awesome shaders.

// ===============================================================================

// ===============================================================================
//#shadermaker includes
//#shadermaker mappings
//#shadermaker functions
// ===============================================================================

//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_progressive_rms_0_02;
uniform vec3 mmv_rms_0_60;
uniform vec3 mmv_rms_0_30;
uniform vec3 mmv_rms_0_20;
uniform vec3 mmv_rms_0_15;
uniform vec3 mmv_rms_0_05;

// Find the distance to some line segment relative to a point.
// The idea is to project the vector starting in one line end to the point relative
// to the line itself, then make that projection value relative to the line's full scale.
// Since it is a line segment, whenever our projection hits more than 1 or less than zero
// means that we're out of bounds, so we clamp that value.
float distance_to_line_segment(vec2 point, vec2 line_start, vec2 line_end) {

    // The vector representing the line segment itself, centered at origin
    // And the unit vector of that segment (vector of length 1)
    vec2 line_vector = line_end - line_start;
    vec2 line_unit_vector = line_vector / length(line_vector);

    // The vector starting from the line segment up to the point
    vec2 line_to_point_vector = point - line_start;

    // Make the projection, that is, project the line to point vector on top
    // of the unit vector of the line (dot product between the two)
    float projection = dot(line_to_point_vector, line_unit_vector);

    // Normalize the projection relative to the line's size
    float projection_normalized = projection / length(line_vector);

    // Clamp this value to 0 and 1 because we're on a line segment
    float walked = clamp(projection_normalized, 0.0, 1.0);

    // Then we need to return the length from the point to the line
    // (A-B yields a vector starting at A and going to B)
    return length(line_to_point_vector - line_vector * walked);
}

// Thick line or not, based on distances
float line(vec2 point, vec2 line_start, vec2 line_end, float thick_min, float thick_max) {
    return 0.0;
    // Distance to the segment
    float away_from_line = distance_to_line_segment(point, line_start, line_end);
    float line_size = length(line_start - line_end);

    // Gradient
    float returned = smoothstep(thick_min, thick_max, away_from_line);

    // Don't draw line based on distance
    // returned *= smoothstep(1.4, 0.5, line_size) + smoothstep(0.05, 0.03, abs(line_size - 0.3));
    return returned;
}

// Noise, 2 inputs, 1 output
float N21(vec2 point) {

    // Compress the space quite heavily, take the fract of it
    point = fract(point * 34.44533 * vec2(432.232, 135.3256));

    // Apply some distortions so we shear the space even more
    point += dot(point, point + 48.8351);

    // Add a dot product for more randomness based off hyperbolas
    return fract(point.x * point.y);
}

// Noise, 2 inputs, 2 outputs
vec2 N22(vec2 point) {

    // Get a base random
    float base = N21(point);

    // Return a vec 2 with the base value and some other random related to that
    return vec2(base, N21(point + base));
}

// Return pseudo random point on grid
vec2 point_on_grid(vec2 grid_id) {
    // Grid noise for random point
    vec2 grid_noise = N22(grid_id);
    
    // Sin of that plus a random starting phase
    float c = mmv_progressive_rms[2] / 400.0;
    return sin((grid_noise * (mmv_time/40.0 + c)) + (grid_noise * 351.34)) * 0.5;
}


float N11(float u) {
    return fract(sin(u) * 33339.1358913);
}

float grid_repr(vec2 grid_id) {
    return N11(sin(grid_id.x + 13.138951 * grid_id.y));
}
float noise(vec2 uv, float size) {
    vec2 grid = uv * size;
    vec2 grid_id = floor(grid);
    grid = fract(grid);
    
    vec2 top = vec2(0.0, 1.0);
    vec2 right = vec2(1.0, 0.0);
    vec2 top_right = vec2(1.0, 1.0);
    
    float this_grid = N11(grid_repr(grid_id));
    float top_grid = N11(grid_repr(grid_id + top));
    float right_grid = N11(grid_repr(grid_id + right));
    float top_right_grid = N11(grid_repr(grid_id + top_right));   
    
    grid = vec2(smoothstep(0.0, 1.0, grid));
    
    float value =
        this_grid * (1.0 - grid.x) * (1.0 - grid.y)
        + right_grid * grid.x * (1.0 - grid.y)
        + top_grid * (1.0 - grid.x) * grid.y
        + top_right_grid * grid.x * grid.y
    ;
    
    return value;
}

float layer_of_noise(int octaves, vec2 uv) {
    float col = 0.0;
    float sum_amplitudes = 0.0;
    
    for (int i = 0; i < octaves; i++) {
        float amplitude = 1.0;
        col += noise(uv, pow(2.0, float(i)));
        sum_amplitudes += amplitude;
    }
    col /= sum_amplitudes;
    return col;
}






vec3 lines_layer(vec2 gluv_all, vec2 raw_gluv_all, int layer_index) {
    //#mmv {"type": "include", "value": "math_constants", "mode": "multiple"}

    vec3 col = vec3(0.0);

    // Make a grid based off OpenGL coordinates with (0, 0) in the middle
    // Standard procedure to some other effects. Also the id is the integer
    // part of the scaled gluv_all coordinates
    vec2 scaled_gluv_all = gluv_all * 5.0;
    vec2 grid_gluv_all = fract(scaled_gluv_all) - 0.5;
    vec2 grid_id = floor(scaled_gluv_all);
    
    // Array for neighbour points positions
    vec2 neighbor_points[9];
    int walk_index = 0;

    // Loop through neighbor cells
    for (int offsetx = -1; offsetx <= 1; offsetx++) {
        for (int offsety = -1; offsety <= 1; offsety++) {

            // Array of offsets
            vec2 offset = vec2(offsetx, offsety);

            // Assign the neighbour point on the array of points plus the offsets
            neighbor_points[walk_index++] = offset + point_on_grid(grid_id + offset);
        }
    }

    // This center grid point
    vec2 this_point = neighbor_points[4];
    float line_thickness_min = 0.005;
    float line_thickness_max = 0.01;

    // Iterate on points
    for (int index = 0; index < 9; index++) {

        // // Sparkle

        float sparkle_brightness = 40.0 - mmv_rms_0_60[2]*25.0; // This acts sorta like the inverse
        float twinkle = 0.5 + 0.5*sin(
            (mmv_time) * (
            5.0 * fract(neighbor_points[index].x)
            + 8.0 * fract(neighbor_points[index].y)
            + 30.0 * layer_index
            ) / 40.0
        );

        // Sparkle implementation
        vec2 close_point = (neighbor_points[index] - grid_gluv_all) * sparkle_brightness;
        
        mat2 flare_rotation = get_rotation_mat2( fract(neighbor_points[index].x) * 2 * PI);
        vec2 flare = close_point * flare_rotation;

        float sparkle = max(0, (1.3*fract(neighbor_points[index].x)) - abs(flare.x * flare.y)) / dot(close_point, close_point)
        + 1.0 / dot(close_point, close_point);
        col += sparkle * twinkle;

        // // Lines

        // Don't draw line to point relative to point
        if (index == 4) {continue;}
    }

    // Stuff we don't catch from grid to grid
    col += line(grid_gluv_all, neighbor_points[1], neighbor_points[3], line_thickness_max, line_thickness_min);
    col += line(grid_gluv_all, neighbor_points[1], neighbor_points[5], line_thickness_max, line_thickness_min);
    col += line(grid_gluv_all, neighbor_points[7], neighbor_points[3], line_thickness_max, line_thickness_min);
    col += line(grid_gluv_all, neighbor_points[7], neighbor_points[5], line_thickness_max, line_thickness_min);

    float color_change_speed = 1.0;
    vec3 color = sin(
        (mmv_progressive_rms_0_02[2]/300.0 + layer_index / 20.0) * color_change_speed
        + raw_gluv_all.yxy + vec3(0.33, 0.66, 0.99)*PI
    ) * 0.5 + 0.5;

    float colnoise = layer_of_noise(4, gluv_all * 10.0 + (1.0 + layer_index));
    
    col *= color*3.0*colnoise;
    col += ((0.14 * color) * (0.5 + mmv_rms_0_05[2]/6.0)) * colnoise;

    return col;
}

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    //#mmv {"type": "include", "value": "math_constants", "mode": "multiple"}
    vec3 col = vec3(0.0);

    // // Render many layers

    // Config
    int n_layers = 6;
    float speed = (((mmv_time / 15.0) + (mmv_progressive_rms_0_02[2]/60.0)) / 7.0) + (mmv_rms_0_30[2] * 0.035);
    float layer_max_size = 0.5;

    vec2 low_freq_shake = vec2(cos(mmv_time*5.0/1.5), sin(mmv_time*8.0/1.5)) / 180.0;
    vec2 high_freq_shake = vec2(cos(mmv_time*10.0/1.3), sin(mmv_time*16.0/1.3)) / 300.0;
    vec2 offset = vec2(sin(mmv_time/7.135135), cos(mmv_time/4.523894)) / 2.0;
    
    // UV
    vec2 layer_uv = gluv_all;
    float length_layer_uv = length(layer_uv);

    // Asymptote at 1
    layer_uv *= ( -(length_layer_uv + mmv_rms_0_05[2] - 0.6) / (length_layer_uv + 1.0) ) + 2.0;

    // Main loop
    for (int layer_index; layer_index < n_layers; layer_index++) {

        // Normalize layer index from 0 to 1
        float layer_index_float_norm = float(layer_index) / float(n_layers);

        // Depth as a function if time
        float depth = fract(layer_index_float_norm + speed);
        float size = mix(layer_max_size, 0.0, depth);
        float fade = (size) * smoothstep(layer_max_size, layer_max_size / 2.0, size);
        mat2 global_rotation = get_rotation_mat2(sin((mmv_time + mmv_progressive_rms[2]) / 200.0));
        
        // Render layer
        col += lines_layer(
            ((layer_uv * global_rotation) + low_freq_shake + high_freq_shake + offset) * pow(size, 0.5) + layer_index,
            gluv_all, layer_index
        ) * fade;
    }


    col = sqrt(col);
    fragColor = vec4(col, 1.0);
}

