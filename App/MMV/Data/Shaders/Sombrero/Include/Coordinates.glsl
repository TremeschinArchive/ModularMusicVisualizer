
// ===============================================================================
// // Coordinates

mat2 m2DRotation2D(float angle) {
    float c = cos(angle);
    float s = sin(angle);
    return mat2(c, s, -s, c);
}

// The ratio relative to the Y coordinate, we expand on X
float mGetNormalizeYratio() { return mResolution.x / mResolution.y; }

// Scalar based on the resolution differing from 1080p (which MMV is developed on)
vec2 mGetFullHDScalar() { return vec2(mResolution.x / 1920, mResolution.y / 1080); }

// How much to rotate the space on interactive mode
mat2 mGetCoordinatesRotation() { return m2DRotation2D(m2DRotation); }

// GL and ST uv based on the aspect ratio
vec2 mGetGLUV() { vec2 gluv = OpenGLUV; gluv.x *= mGetNormalizeYratio(); return gluv; }
vec2 mGetSTUV() { vec2 stuv = ShaderToyUV; stuv.x *= mGetNormalizeYratio(); return stuv; }

// Mouse drag relative to the resolution, flip etc, because m2DDrag is raw pixels
// we want a vec2 normalized to 1 also relative to the aspect ratio
vec2 mGetNormalizedDrag() { 
    vec2 drag = (m2DDrag / mResolution);
    drag *= vec2(-1, mFlip);
    return drag;
}

// ShaderToy UV-like coordinates with zoom, drag applied (interactive)
vec2 mGetSTUVAll() {
    vec2 stuv = mGetSTUV();
    vec2 drag = mGetNormalizedDrag();
    float resratio = mGetNormalizeYratio();
    mat2 rotation = mGetCoordinatesRotation();
    vec2 stuv_zoom = (stuv - vec2(resratio * 0.5, 0.5)) * (m2DZoom * m2DZoom) * rotation + vec2(resratio * 0.5, 0.5);
    return (stuv_zoom) + (drag);
}

// OpenGL UV-like coordinates with zoom, drag applied (interactive)
// and Z-depth illusion. zdepth=1 is the "base" layer
vec2 mGetGLUVParallax(float zdepth) {
    vec2 drag = mGetNormalizedDrag();
    vec2 gluv = mGetGLUV();
    mat2 rotation = mGetCoordinatesRotation();
    return ((gluv * (m2DZoom * m2DZoom)) * rotation) + (drag * 2.0 * zdepth);
}

vec2 mGetGLUVAll() {
    return mGetGLUVParallax(1.0);
}

vec2 mGetSTMouseAbsolute() {
    vec2 m = mMouse;
    m /= mResolution;
    m.x *= mGetNormalizeYratio();
    return m;
}

vec2 mGetGLMouseAbsolute() {
    vec2 m = mMouse;
    m /= mResolution;
    m *= 2;
    m -= vec2(0.5);
    m *= 2;
    m.x *= mGetNormalizeYratio();
    m.y *= -1;
    return m;
}

vec2 mGetGLMouseZoomed() {
    vec2 m = mGetGLMouseAbsolute() * (m2DZoom * m2DZoom);
    m *= mGetCoordinatesRotation();
    m += mGetNormalizedDrag() * 2.0;
    return m;
}

// ===============================================================================
