// ===============================================================================

/// [Include] Sombrero Specification

// ===============================================================================

// // Uniforms

uniform int mFrame;
uniform float mTime;
uniform vec2 mResolution;

uniform float mRotation;
uniform float mZoom;
uniform vec2 mDrag;
uniform int mFlip;

uniform bool mIsDraggingMode;
uniform bool mIsDragging;
uniform bool mIsGuiVisible;
uniform bool mIsDebugMode;

uniform bool mKeyCtrl;
uniform bool mKeyShift;
uniform bool mKeyAlt;

// ===============================================================================

float PI  = 3.14159265358979323846264338;
float TAU = 6.28318530717958647692528676;

// Rotation

mat2 mRotation2D(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat2(c, s, -s, c);
}

// // Coordinates

// The ratio relative to the Y coordinate, we expand on X
float mGetNormalizeYratio() { return mResolution.x / mResolution.y; }

// Scalar based on the resolution differing from 1080p (which MMV is developed on)
vec2 mGetFullHDScalar() { return vec2(mResolution.x / 1920, mResolution.y / 1080); }

// How much to rotate the space on interactive mode
mat2 mGetCoordinatesRotation() { return mRotation2D((-mRotation * PI) / 180.0); }

// GL and ST uv based on the aspect ratio
vec2 mGetGLUV() { vec2 gluv = opengl_uv; gluv.x *= mGetNormalizeYratio(); return gluv;}
vec2 mGetSTUV() { vec2 stuv = shadertoy_uv; stuv.x *= mGetNormalizeYratio(); return stuv;}

// Mouse drag relative to the resolution, flip etc, because mDrag is raw pixels
// we want a vec2 normalized to 1 also relative to the aspect ratio
vec2 mGetMouseDrag() { 
    vec2 drag = (mDrag / mResolution);
    drag.x *= - mGetNormalizeYratio();
    drag.y *= mFlip; 
    return drag;
}

// ShaderToy UV-like coordinates with zoom, drag applied (interactive)
vec2 mGetSTUVAll() {
    vec2 stuv = mGetSTUV();
    vec2 drag = mGetMouseDrag();
    float resratio = mGetNormalizeYratio();
    mat2 coordinates_rotation = mGetCoordinatesRotation();
    vec2 stuv_zoom = (stuv - vec2(resratio * 0.5, 0.5)) * (mZoom * mZoom) * coordinates_rotation + vec2(resratio * 0.5, 0.5);
    vec2 stuv_drag = stuv + (drag / 4.0);
    return (stuv_zoom) + (drag);
}

// OpenGL UV-like coordinates with zoom, drag applied (interactive)
vec2 mGetGLUVAll() {
    vec2 gluv = mGetGLUV();
    vec2 drag = mGetMouseDrag();
    mat2 coordinates_rotation = mGetCoordinatesRotation();
    vec2 gluv_zoom = gluv * (mZoom * mZoom);
    vec2 gluv_drag = gluv + (drag * 2.0);
    return (gluv_zoom * coordinates_rotation) + (drag * 2.0);
}

// // Noise

float mN21(vec2 coords) {
   return fract(sin(dot(coords.xy, vec2(18.4835183, 59.583596))) * 39758.381532);
}

// Utils

// A is proportional to B
// C is proportional to what?
// what = b*c / a for a \neq 0
float mProportion(float a, float b, float c) {
    return (b * c) / a;
}

// Alpha composite new and old layers
vec4 mAlphaComposite(vec4 old, vec4 new) {
    return mix(old, new, new.a);
}

// Saturation
vec4 mSaturate(vec4 col, float amount) {
    return clamp(col * amount, 0.0, 1.0);
}

float mAtan2(in float y, in float x) {
    if (y < 0) {
        return (2 * 3.14159265) - atan(-y, x);
    } else {
        return atan(y, x);
    }
}

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
