// ===============================================================================
//                                 GPL v3 License                                
// ===============================================================================
//
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
//
// ===============================================================================
//
// Purpose: MMV specifications that are imported when making one main GLSL file
// for rendering
//
// ===============================================================================
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation, either version 3 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along with
// this program. If not, see <http://www.gnu.org/licenses/>.
//
// ===============================================================================

// // Useful function

// https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83
float rand(float n){return fract(sin(n) * 43758.5453123);}

// Blit one image on the canvas, see function arguments
vec4 mmv_blit_image(
        in vec4 canvas,     // Return this if out of bounds and repeat = false
        in sampler2D image, // The texture
        in vec2 image_resolution,  // For ratios
        in vec2 uv,         // UV we're getting (usually the layer's uv)
        in vec2 anchor,     // Anchor the rotation on the screen in some point
        in vec2 shift,      // Shift the image (for example vec2(0.5, 0.5) will rotate around the center)
        in float scale,     // Scale of the image 1 = 100%, 2 = 200%
        in float angle,     // Angle of rotation, be aware of aliasing!
        in bool repeat)     // If out of bounds tile the image?
    {
    
    // Image ratios
    float image_ratio_x = image_resolution.x / image_resolution.y;
    float image_ratio_y = image_resolution.y / image_resolution.x;

    // Scale matrix
    mat2 scale_mateix = mat2(
        (1.0 / scale), 0,
        0, (1.0 / scale)
    );

    // Rotation Matrix
    float c = cos(angle);
    float s = sin(angle);
    mat2 rotation_matrix = mat2(
         c * image_ratio_y, s * image_ratio_x,
        -s, c
    );

    // The rotated, scaled and anchored, flipped and shifted UV coordinate to get this sampler2D texture
    vec2 get_image_uv = (rotation_matrix * scale_mateix * (uv - anchor)) + shift;

    // If not repeat, check if any uv is out of bounds
    if (!repeat) {
        if (get_image_uv.x < 0.0) { return canvas; }
        if (get_image_uv.x > 1.0) { return canvas; }
        if (get_image_uv.y < 0.0) { return canvas; }
        if (get_image_uv.y > 1.0) { return canvas; }
    }

    // // Multi sampling for removing jagged edges
    float center_intensity = 5.0;

    // Get the texture (raw pixel, the center, non anti aliased)
    vec4 imagepixel = texture(image, get_image_uv);
    imagepixel *= center_intensity;

    // // Multi sample config

    // Distance of the uv texture on this pixel to averate out stuff
    float lookup = (((1 / mmv_resolution.x) + (1 / mmv_resolution.y))/2.0) * 2.0;

    // How many random pixels around to average
    float many = 1;

    // Constant
    float tau = 3.1415*2;
    vec4 multisampled = imagepixel;

    // The vector we get the translated one given the rotation point
    vec2 get_lookuped = vec2(0.0);

    // Iterate
    for (float i = 0.0; i < tau; i += tau / many) {{
        // A random radially point
        get_lookuped = get_image_uv + (vec2(rand(i), rand(i+1)) * lookup);
        multisampled += texture(image, get_lookuped);
    }}

    imagepixel = multisampled / (many + center_intensity);

    // Return the texture
    return imagepixel;
}

