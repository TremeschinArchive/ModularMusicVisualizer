// ===============================================================================
//                                 GPL v3 License                                
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
// See LICENSE.md, this is compact header for not cluttering final shaders
// ===============================================================================

// Test safe against multiple includes on the same file, should only replace the
// first one and ignore the second one
#pragma include mmv_specification once;
#pragma include mmv_specification once;

void main() {

    // Test include for usage stuv and gluv normalized according to the aspect ratio
    // UV coordinates, one from ShaderToy (ST UV) and other from OpenGL UV (GL UV)
    // Shadertoy bottom left is (0, 0) and OpenGL all corners max out ad 1 or -1
    #pragma include coordinates_normalization multiple;

    // "Random" colors testing, we should see mirrored red on the left and right
    // part of the screen since that is using abs(gluv.x), blue should increase
    // to the top and green should be turning on and off
    vec4 col = vec4(abs(gluv.x), abs(sin(0.5*mmv_time)), gluv.y, 1.0);

    // Output the color
    fragColor = col;
}
