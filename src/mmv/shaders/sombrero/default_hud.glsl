
vec4 mainImage() {
    vec4 col = vec4(0.0);
    vec2 stuv_all = mGetSTUVAll();
    vec2 gluv_all = mGetGLUVAll();
    vec2 fulldh_scalar = mGetFullHDScalar();
    float resratio = mGetNormalizeYratio();

    // Coordinates ST, GL uv
    if (mIsDebugMode) {
        float line_size = 0.004;
        float alpha = 0.8;

        // ShaderToy coordinates, red and green
        if (abs(stuv_all.x) < line_size) { col = mAlphaComposite(col, vec4(1, 0.0, 0.0, alpha)); }
        if (abs(stuv_all.y) < line_size) { col = mAlphaComposite(col, vec4(0.0, 1.0, 0.0, alpha)); }

        // OpenGL coordinates, cyan and blue
        if (abs(gluv_all.x) < line_size * 2) { col = mAlphaComposite(col, vec4(0.0, 0.0, 1.0, alpha)); }
        if (abs(gluv_all.y) < line_size * 2) { col = mAlphaComposite(col, vec4(0.0, 1.0, 1.0, alpha)); }
    }

    // Crosshair
    if (mIsDraggingMode) {
        float line_size = 0.002;
        float border = 0.001;
        float size = 0.02;

        // Rotation marker
        if (mKeyAlt) {
            if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size * 1.6) {
                col = mAlphaComposite(col, vec4(0.0, 1.0, 0.0, 1.0));
            }

            if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size * 1.6 / resratio) {
                col = mAlphaComposite(col, vec4(0.0, 1.0, 0.0, 1.0));
            }
        }

        // Draw center cross
        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mAlphaComposite(col, vec4(1, 1, 1, 1.0));
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mAlphaComposite(col, vec4(1, 1, 1, 1.0));
        }

        // While dragging crosshair changes color
        if (mIsDragging) {
            if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
                col = mAlphaComposite(col, vec4(1, 1.0, 0.0, 1.0));
            }

            if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
                col = mAlphaComposite(col, vec4(1.0, 1.0, 0, 1.0));
            }
        }

        // Draw border
        line_size += border;

        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mAlphaComposite(vec4(0.0, 0.0, 0.0, 0.8), col);
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mAlphaComposite(vec4(0.0, 0.0, 0.0, 0.8), col);
        }

        // Markers
        line_size += 4 * border;

        // Zoom marker
        if (mKeyShift) {
            if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
                col = mAlphaComposite(vec4(1.0, 0.0, 0.0, 1.0), col);
            }

            if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
                col = mAlphaComposite(vec4(1.0, 0.0, 0.0, 1.0), col);
            }
        }
    }

    // Alignment stuff while dragging and ctrl pressed
    if (mKeyCtrl) {

        // Ultra thin bars across screen
        float across_screen_alpha = 0.9;
        int alignment_grid_N = 4;
        vec3 alignment_color = vec3(1.0);

        float stepp = 1.0 / float(alignment_grid_N/2);

        // 2.3 because floating point..
        for (float i = -1 + stepp; i < 1; i += stepp) {
            for (float k = -1 + stepp; k < 1; k += stepp) {
                if (abs(opengl_uv.x - i) < 2.3 / mResolution.x) {
                    col = mAlphaComposite(col, vec4(alignment_color, across_screen_alpha));
                }

                if (abs(opengl_uv.y - k) < 2.3 / mResolution.y) {
                    col = mAlphaComposite(col, vec4(alignment_color, across_screen_alpha));
                }
            }
        }
    }

    // Gui focus
    if (mIsGuiVisible) {
        // col = mAlphaComposite(col, vec4(0.0, 0.0, 0.0, 0.486));
    }

    return col;
}
