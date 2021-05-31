
// ===============================================================================
// // Utils

// A is proportional to B
// C is proportional to what?
// what = b*c / a for a \neq 0
float mProportion(float a, float b, float c) {
    return (b * c) / a;
}

// Alpha composite new and old layers
vec4 mAlphaComposite(vec4 old, vec4 new) {
    vec4 src = new;
    vec4 dst = old;

    // Final Alpha
    float A = src.a + dst.a * (1.0 - src.a);
    return vec4(
        // Premultiply         Premultiply but 1.0 - src alpha     Final alpha
        ( (src.rgb * src.a) + (dst.rgb * dst.a * (1.0 - src.a)) ), A
    );
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

// float to bool
bool f2bool(float f) { return f > 0.5; }

// ===============================================================================
