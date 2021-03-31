
// ===============================================================================

/// [Include] Coordinates normalization

// The ratio relative to the Y coordinate, we expand on X
float resratio = (mmv_resolution.x / mmv_resolution.y);

// OpenGL and Shadertoy UV coordinates, GL goes from -1 to 1 on every corner
// and Shadertoy uses bottom left = (0, 0) and top right = (1, 1).
// glub and stuv are normalized relative to the height of the screen, they are
// respective the Opengl UV and Shadertoy UV you can use

// // Normalization

// Normalize the OpenGL coord to gluv (GL UV)
vec2 gluv = opengl_uv;
gluv.x *= resratio;

// Normalize the Shadertoy coord to stuv (ShaderToy UV)
vec2 stuv = shadertoy_uv;
stuv.x *= resratio;

// Zoomed uv coords, STUV is a bit trickier since we have to transpose the center to the center of 
// the screenm apply zoom then revert
vec2 gluv_zoom = gluv * (mmv_zoom * mmv_zoom);
vec2 stuv_zoom = (stuv - vec2(0.5, 0.5)) * (mmv_zoom * mmv_zoom) + vec2(0.5, 0.5);

// Mouse drag
vec2 drag = (mmv_drag / mmv_resolution);
drag.x *= -resratio;
drag.y *= mmv_flip; 

// Since the areas of GLUV = 4*STUV we only apply half the drag to ST* stuff

// GL and ST uv coordinates with drag
vec2 gluv_drag = gluv + (drag * 2.0);
vec2 stuv_drag = stuv + (drag / 4.0);

// GL and ST uv coordinates with drag + zoom
vec2 gluv_zoom_drag = gluv_zoom + (drag * 2.0);
vec2 stuv_zoom_drag = stuv_zoom + (drag);


// [Normally you'd use the shadertoy_uv for reading textures to fullscreen]

// // Max values [left X, right X, bottom Y, top Y]

vec4 gluv_boundaries = vec4(-1 * resratio, 1 * resratio, -1, 1);
vec4 stuv_boundaries = vec4( 0 * resratio, 1 * resratio,  0, 1);

// The Y components are either 1, 0 or -1 ("static") because our resratio is X/Y
// and we keep the Y coordinates fixed on those points so we only deal with horizontal
// stretching and don't care for the Y component

// // Transformations, usually will be applied globally

//#shadermaker transformations

// ===============================================================================
