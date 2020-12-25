//!HOOK SCALED
//!BIND HOOKED

vec4 hook() {
    vec4 o = HOOKED_tex(HOOKED_pos);
    float multiple = 16;
    
    o.r = (int((o.r*256) / multiple) * multiple) / 256; 
    o.g = (int((o.g*256) / multiple) * multiple) / 256; 
    o.b = (int((o.b*256) / multiple) * multiple) / 256; 

    return o;
} 
