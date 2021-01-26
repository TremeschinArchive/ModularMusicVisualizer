
// ===============================================================================
//                                 GPL v3 License                                
// Copyright (c) 2020 - 2021,
//   - Tremeschin < https://tremeschin.gitlab.io > 
// See LICENSE.md, this is compact header for not cluttering final shaders
// ===============================================================================
// // // // Coordinates normalization

// The ratio relative to the Y coordinate, we expand on X
float resratio = (mmv_resolution.y / mmv_resolution.x);

// OpenGL and Shadertoy UV coordinates, GL goes from -1 to 1 on every corner
// and Shadertoy uses bottom left = (0, 0) and top right = (1, 1).
// glub and stuv are normalized relative to the height of the screen, they are
// respective the Opengl UV and Shadertoy UV you can use

// Normalize the OpenGL coord to gluv (GL UV)
vec2 gluv = opengl_uv;
gluv.x *= resratio;

// Normalize the Shadertoy coord to stuv (ShaderToy UV)
vec2 stuv = shadertoy_uv;
stuv.x *= resratio;

// Normally you'd use the shadertoy_uv for reading textures to fullscreen

// // // //
