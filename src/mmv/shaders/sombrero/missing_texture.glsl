vec4 mainImage() {
    // ===============================================================================

    // This is the fallback shader when something went wrong, check console output
    // for errors as well as the log of the faulty shader.

    // ===============================================================================

    vec2 stuv_all = mGetSTUVAll();

    // Transpose
    stuv_all += vec2(mTime / 64.0, mTime / 64.0);

    // Empty col
    vec4 col = vec4(0.0);

    // Grid
    float size = 16.0;

    // Raw resolution to uv normalized based on grid size
    vec2 pixel = 6.0 / mResolution;

    // Kernel size 5
    for (int x = -5; x < 5; x++) {
        for (int y = -5; y < 5; y++) {

            vec2 test_magenta_uv = floor( size * stuv_all + dot(pixel, vec2(x, y)) );

            if (mod(test_magenta_uv.x + test_magenta_uv.y, 2.0) == 0.0) {
                // Add color divided by kernel area and decrease when away from center
                col += (vec4(1.0, 0.0, 1.0, 0.5) / 25.0) * (1.0 - sqrt(x*x + y*y) / 5.0);
            }

        }
    }

    return col;
}