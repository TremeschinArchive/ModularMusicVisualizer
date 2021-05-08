
vec4 mainImage() {
    vec2 gluv_all = mGetGLUVAll();
    vec2 stuv_all = mGetSTUVAll();
    
    vec4 c = vec4(0.0);
    float grid = 50;
    float offs = mTime;
    if (sin(stuv_all.x * (0.2 + stuv_all.y) * grid  + offs) > sin(stuv_all.y * grid )) {
        c = vec4(1.0);
    }
    vec4 col = c * (1.0 - stuv_all.y);

    // col = vec4(0.0, 0.0, 0.0, 1.0);
    
    float angle = mAtan2(gluv_all.y, gluv_all.x) + mTime;
    vec4 hsved = mHSV2RGB(vec4(angle, 1.0, 1, 1));
    float d = length(gluv_all);

    float r = 0.7;

    if (d > r) {
        float ring = (r)/d;
        col = mAlphaComposite(col, hsved * pow(ring, 2.0));
    } else {
        float ring = pow(d/r, 12.0);
        // col = mAlphaComposite(col, hsved * ring);
        col = hsved * ring;
    }
    
    return col;
}
