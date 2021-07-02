
// ===============================================================================
// // Colors

// https://www.rapidtables.com/convert/color/hsv-to-rgb.html
// "Assume 0 <= H < 2pi, 0 < S <= 1, 0 < V <= 1"
// I don't know much colorspaces but this seems fun to use
vec3 mHSV2RGB(vec3 hsv) {
    float h = hsv.x; float s = hsv.y; float v = hsv.z;
    h = mod(h, 2*PI);
    float c = v * s;
    float x = c * (1 - abs( mod(h / (PI/3), 2) - 1 ));
    float m = v - c;
    vec3 rgb = vec3(0.5);
    switch (int(floor( 6*(h/(2*PI)) ))) {
        case 0: rgb = vec3(c, x, 0); break;
        case 1: rgb = vec3(x, c, 0); break;
        case 2: rgb = vec3(0, c, x); break;
        case 3: rgb = vec3(0, x, c); break;
        case 4: rgb = vec3(x, 0, c); break;
        case 5: rgb = vec3(c, 0, x); break;
        default: rgb = vec3(0.0);
    }
    return rgb + vec3(m);
}
// For vec4
vec4 mHSV2RGB(vec4 hsva){ return vec4(mHSV2RGB(hsva.rgb), hsva.a); }

// ===============================================================================
