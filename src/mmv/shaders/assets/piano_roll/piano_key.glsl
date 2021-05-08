
vec4 mainImage() {
    vec4 c = vec4(0.0);
      
    if (abs(opengl_uv.x) < 0.5 && abs(opengl_uv.y) < 0.5) {
        if (f2bool(is_playing)) {
            c = vec4(1.0, 0.9843, 0.0, 1.0);
        } else{
            if (f2bool(is_white)) {
                c = vec4(1.0);
            } else {
                c = vec4(vec3(0.0), 1.0);
            }
        }
    } else {
        if (f2bool(is_playing) && abs(opengl_uv.y) > 0.5) {
            c = vec4( vec3(1.0, 0.9843, 0.0), 1.0 - opengl_uv.y);
        }  
    }

    c.rgb *= (opengl_uv.y + 1) / 2;
    return c;
}