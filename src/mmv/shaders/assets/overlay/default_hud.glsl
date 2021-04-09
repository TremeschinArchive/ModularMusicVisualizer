
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // Crosshair
    if (is_dragging) {
        float line_size = 0.002;
        float border = 0.001;
        float size = 0.02;

        // Draw center cross
        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mmv_alpha_composite(col, vec4(1, 1, 1, 1.0));
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mmv_alpha_composite(col, vec4(1, 1, 1, 1.0));
        }

        // Draw border
        line_size += border;

        if (abs(opengl_uv.x) < (line_size / fulldh_scalar.y) / resratio && abs(opengl_uv.y) < size) {
            col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.8));
        }

        if (abs(opengl_uv.y) < line_size / fulldh_scalar.y && abs(opengl_uv.x) < size / resratio) {
            col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.8));
        }

        // Alignment stuff while dragging and ctrl pressed
        if (mmv_key_ctrl) {
            // Ultra thin bars across screen
            float across_screen_alpha = 0.5;
            if (abs(opengl_uv.x) < 1.5 / mmv_resolution.x) {
                col = mmv_alpha_composite(col, vec4(0, 0, 0, across_screen_alpha));
            }

            if (abs(opengl_uv.y) < 1.5 / mmv_resolution.y) {
                col = mmv_alpha_composite(col, vec4(0, 0, 0, across_screen_alpha));
            }
        }
    }

    // Coordinates ST, GL uv
    if (mmv_debug_mode) {
        float line_size = 0.004;
        float alpha = 0.8;

        // ShaderToy coordinates, red and green
        if (abs(stuv_all.x) < line_size) { col = mmv_alpha_composite(col, vec4(1, 0.0, 0.0, alpha)); }
        if (abs(stuv_all.y) < line_size) { col = mmv_alpha_composite(col, vec4(0.0, 1.0, 0.0, alpha)); }

        // OpenGL coordinates, cyan and blue
        if (abs(gluv_all.x) < line_size * 2) { col = mmv_alpha_composite(col, vec4(0.0, 0.0, 1.0, alpha)); }
        if (abs(gluv_all.y) < line_size * 2) { col = mmv_alpha_composite(col, vec4(0.0, 1.0, 1.0, alpha)); }
    }

    // Gui focus
    if (is_gui_visible) {
        col = mmv_alpha_composite(col, vec4(0.0, 0.0, 0.0, 0.486));
    }

    fragColor = col;
}

