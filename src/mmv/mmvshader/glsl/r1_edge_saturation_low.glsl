//!HOOK SCALED
//!BIND HOOKED

vec4 hook() {

    vec2 center = vec2(0.5, 0.5);

    vec2 polar = HOOKED_pos - center;
    // float r = pow(pow(polar.y, 2.0) + pow(polar.x, 2.0), 0.5);
    float r = pow(pow(polar.y, 2.0) + pow(polar.x, 2.0), 0.2);

    vec4 video = HOOKED_tex(HOOKED_pos);

    // float ratio_here = 1.0 - (r);
    float avg = (video.r + video.g + video.b) / 3.0;

    float sat = 1.4;
    video.r = ((avg - video.r) * (r)) + video.r;
    video.g = ((avg - video.g) * (r)) + video.g;
    video.b = ((avg - video.b) * (r)) + video.b;

    return video;
}

