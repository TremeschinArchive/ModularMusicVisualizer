
// ===============================================================================
// // Ray Marching Camera

vec3 m3DRayMarchRayOrigin(){ return m3DCameraPos.xzy; }

vec3 m3DRayMarchRayDirection(){
    vec2 uv = mGetGLUV();
    return normalize(((m3DCameraPointing) + ((m3DCameraBase[1]*uv.y) + (m3DCameraBase[2]*uv.x)) * m3DFOV).xzy);
}

// ===============================================================================
// // Signed Distance Functions

//  Camera ..
//    y|     .........
// ____|______________o____________
// float m3DSDFPlane(vec3 point) {

// }

// Minimum distance to a sphere
//              ( )
// O          (   C )
// · ----->  ( R o   )
//      L     (     )
//              ( )
// From point O to sphere center C, then subtract the radius
float m3DSDFSphere(vec3 point, vec3 sphere_center, float sphere_radius) {
    return length(sphere_center - point) - sphere_radius;
}