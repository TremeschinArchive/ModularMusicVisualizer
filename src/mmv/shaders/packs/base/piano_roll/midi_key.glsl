
vec4 mainImage(in vec2 fragCoord) {

    // return vec4(0, PI/3, 2*PI/3, 1) + vec4(note);

    vec4 c = vec4(mix(vec3(1.0, 0.0, 0.0), vec3(1.0, 0.6, 0.0), shadertoy_uv.y), 1.0);

    if (abs(opengl_uv.x) < 0.5 && abs(opengl_uv.y) < 0.5) {
        return c;
    } else{
        return vec4(c.rgb, 0.8 * (1.0 - max(abs(opengl_uv.x), abs(opengl_uv.y))));
    }
}