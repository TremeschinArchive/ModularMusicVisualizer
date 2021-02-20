// ===============================================================================
//                                 GPL v3 License                                
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
// See LICENSE.md, this is compact header for not cluttering final shaders
//
// Jumpcutter extension for MMV, only draw whatever texture we piped to the shader
//
// ===============================================================================

#pragma map name jumpcutter_glsl
#pragma map video=pipeline_texture;;{WIDTH}x{HEIGHT}x3

void main() {
    #pragma include coordinates_normalization multiple
    vec4 col = texture(video, shadertoy_uv);
    fragColor = col.bgra;
}
