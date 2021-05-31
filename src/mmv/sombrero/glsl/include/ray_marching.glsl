
// ===============================================================================
// // Ray Marching

vec3 m3DRayMarchRayOrigin(){ return m3DCameraPos.xzy; }

vec3 m3DRayMarchRayDirection(){
    vec2 uv = mGetGLUV();
    return normalize(((m3DCameraPointing) + ((m3DCameraBase[1]*uv.y) + (m3DCameraBase[2]*uv.x)) * m3DFOV).xzy);
}

// ===============================================================================
