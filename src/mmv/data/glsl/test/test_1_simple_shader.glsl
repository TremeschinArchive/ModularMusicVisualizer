// ===============================================================================
//                                 GPL v3 License                                
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
// See LICENSE.md, this is compact header for not cluttering final shaders
// ===============================================================================

// Test safe against multiple includes on the same file, should only replace the
// first one and ignore the second one
#pragma include mmv_specification;
#pragma include mmv_specification;

void main() {

    // Test include for usage stuv and gluv
    #pragma include coordinates_normalization;

    // "Random" colors testing, we should see mirrored red on the left and right
    // part of the screen since that is using abs(gluv.x), blue should increase
    // to the top and green should be turning on and off
    vec4 col = vec4(abs(gluv.x), abs(sin(0.5*mmv_time)), gluv.y, 1.0);

    // Output the color
    fragColor = col;
}
