
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // Coordinates ST, GL uv
    if (mmv_debug_mode) {
        float line_size = 0.004;
        float alpha = 0.8;

        // ShaderToy coordinates, red and green
        if (abs(stuv_all.x) < line_size) { col = mmv_alpha_composite(vec4(1, 0.0, 0.0, alpha), col); }
        if (abs(stuv_all.y) < line_size) { col = mmv_alpha_composite(vec4(0.0, 1.0, 0.0, alpha), col); }

        // OpenGL coordinates, cyan and blue
        if (abs(gluv_all.x) < line_size * 2) { col = mmv_alpha_composite(vec4(0.0, 0.0, 1.0, alpha), col); }
        if (abs(gluv_all.y) < line_size * 2) { col = mmv_alpha_composite(vec4(0.0, 1.0, 1.0, alpha), col); }
    }

    // Crosshair
    if (is_dragging) {
        float line_size = 0.002;
        float border = 0.001;
        float size = 0.02;

        // Rotation marker
        if (mmv_key_alt) {
            if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size * 1.6) {
                col = mmv_alpha_composite(vec4(0.0, 1.0, 0.0, 1.0), col);
            }

            if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size * 1.6 / resratio) {
                col = mmv_alpha_composite(vec4(0.0, 1.0, 0.0, 1.0), col);
            }
        }

        // Draw center cross
        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mmv_alpha_composite(vec4(1, 1, 1, 1.0), col);
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mmv_alpha_composite(vec4(1, 1, 1, 1.0), col);
        }

        // Draw border
        line_size += border;

        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.8));
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.8));
        }

        // Markers
        line_size += 4 * border;

        // Zoom marker
        if (mmv_key_shift) {
            if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
                col = mmv_alpha_composite(col, vec4(1.0, 0.0, 0.0, 1.0));
            }

            if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
                col = mmv_alpha_composite(col, vec4(1.0, 0.0, 0.0, 1.0));
            }
        }
    }

    // Alignment stuff while dragging and ctrl pressed
    if (mmv_key_ctrl) {

        // Ultra thin bars across screen
        float across_screen_alpha = 0.5;
        int alignment_grid_N = 4;

        for (float i = -1; i < 1; i += 1.0 / float(alignment_grid_N/2)) {
            for (float k = -1; k < 1; k += 1.0 / float(alignment_grid_N/2)) {
                if (abs(opengl_uv.x - i) < 1.5 / mmv_resolution.x) {
                    col = mmv_alpha_composite(vec4(0, 0, 0, across_screen_alpha), col);
                }

                if (abs(opengl_uv.y - k) < 1.5 / mmv_resolution.y) {
                    col = mmv_alpha_composite(vec4(0, 0, 0, across_screen_alpha), col);
                }
            }
        }
    }

    // Gui focus
    if (is_gui_visible) {
        col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.486));
    }

    fragColor = col;
}

