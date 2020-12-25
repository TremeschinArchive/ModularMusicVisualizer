//!HOOK SCALED
//!BIND HOOKED

vec4 hook() {
    vec4 o = HOOKED_tex(HOOKED_pos);
    float avg = (o.r + o.g + o.b) / 3.0;
    o.rgb = vec3(avg, avg, avg); 
    return o;
} 
