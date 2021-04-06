
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_rms_0_20;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // col.rg = gluv_all.xy;

    // int total = mmv_waveform_width * mmv_waveform_height;

    // float where = stuv_all.x * mmv_waveform_width * mmv_waveform_height;

    // ivec2 get_waveform = ivec2(
    //     mod(where, mmv_waveform_width),
    //     int(where / mmv_waveform_width)
    // );

    vec2 center = gluv_all - vec2(0.0, 0.5);
    vec2 offset = vec2(mod(1/60, mmv_time), 0) * coordinates_rotation;
    ivec2 get_waveform = ivec2(int(mmv_waveform_width * ((gluv_all.x - vec2(-resratio, 0) - offset)/2 / resratio) ), 0.0);
    vec4 mmv_waveform_l = 0.002 + pow( abs(texelFetch(mmv_waveform, get_waveform, 0)), vec4(0.3));
    // vec4 mmv_waveform_l = 0.002 + pow( abs(texture(mmv_waveform, shadertoy_uv)) * 0.4, vec4(0.3));
    
    // vec4 mmv_waveform_l = texture(mmv_waveform, vec2(stuv_all.x, 0));

    // col = mmv_waveform_l;

    // if ( gluv_all.y > mmv_waveform_l.x) {
        // col += vec4(1.0);
    // } 

    mmv_waveform_l *= 0.6;
    float dist = abs(center.y);

    if ( dist < mmv_waveform_l.x) {
        float v = dist * mmv_waveform_l.x * 4;
        col += vec4(v, 0.0, 0.0, 0.25);
        // col += vec4(0.0118, 0.0118, 0.0392, 1.0);
    } 

    if ( dist < mmv_waveform_l.y) {
        float v = dist * mmv_waveform_l.x * 4;
        col += vec4(v, 0.0, 0.0, 0.25);
        // col += vec4(0.0118, 0.0118, 0.0392, 1.0);
    } 

    // if ( abs(center.y) < mmv_waveform_l.x) {
    //     col += vec4(0.0, 0.0, 0.0, 0.4);
    // } 

    // if ( abs(center.y) < mmv_waveform_l.y) {
    //     col += mmv_alpha_composite(vec4(0.0, 0.7176, 1.0, 0.4), col);
    // } 


    fragColor = col;
}

