//!HOOK SCALED
//!BIND HOOKED

vec4 hook() {

    vec2 center = vec2(0.5, 0.5);

    vec2 polar = HOOKED_pos - center;
    float r = pow(pow(polar.y, 2.0) + pow(polar.x, 2.0), 0.5);

    vec4 video = HOOKED_tex(HOOKED_pos);

    float ratio_here = 1.0 - (r/1.5);
    float avg = (video.r + video.g + video.b) / 3.0;

    video.r = ((avg - video.r) * (r/2)) + video.r;
    video.g = ((avg - video.g) * (r/2)) + video.g;
    video.b = ((avg - video.b) * (r/2)) + video.b;

    video.rgb *= ratio_here;

    return video;
}

