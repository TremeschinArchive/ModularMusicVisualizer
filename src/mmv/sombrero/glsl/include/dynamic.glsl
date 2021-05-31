
// ===============================================================================
// // "Dynamic"

// Blit one image on the canvas, see function arguments
vec4 mBlitImage(
        in vec4 canvas,            // Return this if out of bounds and repeat = false
        in sampler2D image,        // The texture
        in vec2 image_resolution,  // to keep aspect ratio, see *1
        in vec2 uv,                // UV we're getting (usually the layer's uv)
        in vec2 anchor,            // Anchor the rotation on the screen in some point
        in vec2 shift,             // Shift the image (for example vec2(0.5, 0.5) will rotate around the center)
        in float scale,            // Scale of the image 1 = 100%, 2 = 200%
        in float angle,            // Angle of rotation, be aware of aliasing!
        in bool repeat,            // If out of bounds tile the image?
        in bool undo_gamma,        // Is the image already gamma corrected? usually (99% the time) True
        in float gamma)            // Gamma value to revert, only used if undo_gamma is True, usually set to 2
    {
    
    // 1. PLEASE, IF YOU ARE USING DYNSHADER REAL TIME SEND MMV_RESOLUTION RATHER THAN THIS OBJECT'S RESOLUTION
    // OTHERWISE IT'LL NOT SCALE ACCORDINGLY, LEAVING THIS OBJECT'S RESOLUTION WORKS FOR HEADLESS.
    // I say this because it took me 3h of headache until I noticed the problem.

    // Image ratios
    float image_ratioY = image_resolution.y / image_resolution.x;
    float image_ratioX = image_resolution.x / image_resolution.y;

    // Scale according to X's proportion (increase rotation matrix ellipse)
    scale *= image_ratioX;
    
    // Scale matrix
    mat2 scale_matrix = mat2(
        (1.0 / scale) * image_ratioX, 0,
        0, -(1.0 / scale)
    );

    // Rotation Matrix
    float c = cos(angle);
    float s = sin(angle);
    mat2 rotation_matrix = mat2(
         c / image_ratioX, s,
        -s, c / image_ratioY
    );

    // The rotated, scaled and anchored, flipped and shifted UV coordinate to get this sampler2D texture
    vec2 get_image_uv = (rotation_matrix * scale_matrix * (uv - anchor)) + shift;

    // If not repeat, check if any uv is out of bounds
    if (!repeat) {
        if (get_image_uv.x < 0.0) { return canvas; }
        if (get_image_uv.x > 1.0) { return canvas; }
        if (get_image_uv.y < 0.0) { return canvas; }
        if (get_image_uv.y > 1.0) { return canvas; }
    }
    // Get the texture (raw pixel, the center, non anti aliased)
    vec4 imagepixel = texture(image, get_image_uv);

    // Return the square of image pixel colors
    if (undo_gamma) {
        imagepixel = pow(imagepixel, vec4(gamma));
    }

    // Return the texture
    return imagepixel;
}

// ===============================================================================
