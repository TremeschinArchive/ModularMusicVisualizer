
//#mmv {"type": "include", "value": "mmv_specification", "mode": "once"}

uniform vec3 mmv_rms_0_20;

void main() {
    //#mmv {"type": "include", "value": "coordinates_normalization", "mode": "multiple"}
    vec4 col = vec4(0.0);

    // col.rg = gluv_all.xy;

    // int total = mmv_rms_waveforms_width * mmv_rms_waveforms_height;

    // float where = stuv_all.x * mmv_rms_waveforms_width * mmv_rms_waveforms_height;

    // ivec2 get_waveform = ivec2(
    //     mod(where, mmv_rms_waveforms_width),
    //     int(where / mmv_rms_waveforms_width)
    // );

    vec2 center = gluv_all;// - vec2(0.0, 0.5);
    vec2 offset = vec2(mod(1/60, mmv_time), 0) * coordinates_rotation;
    ivec2 get_waveform = ivec2(int(mmv_rms_waveforms_width * ((gluv_all.x - vec2(-resratio, 0) - offset)/2 / resratio) ), 0.0);
    vec4 mmv_rms_waveforms = 0.002 + pow( abs(texelFetch(mmv_rms_waveforms, get_waveform, 0)), vec4(0.3));
    vec4 mmv_mean_waveforms = 0.002 + pow( abs(texelFetch(mmv_mean_waveforms, get_waveform, 0)), vec4(0.3));
    // vec4 mmv_rms_waveforms = 0.002 + pow( abs(texture(mmv_rms_waveforms, shadertoy_uv)) * 0.4, vec4(0.3));
    
    // vec4 mmv_rms_waveforms = texture(mmv_rms_waveforms, vec2(stuv_all.x, 0));

    // col = mmv_rms_waveforms;

    // if ( gluv_all.y > mmv_rms_waveforms.x) {
        // col += vec4(1.0);
    // } 

    mmv_rms_waveforms *= 0.1;
    mmv_mean_waveforms *= 0.3;
    float dist = abs(center.y);

    if ( dist < mmv_rms_waveforms.x) { col += vec4(0.0, 0.0, 0.0, 0.09); } 
    if ( dist < mmv_rms_waveforms.y) { col += vec4(0.0, 0.0, 0.0, 0.09); } 

    if ( dist < mmv_mean_waveforms.x) { col += vec4(0.0, 0.0, 0.0, 0.25); } 
    if ( dist < mmv_mean_waveforms.y) { col += vec4(0.0, 0.0, 0.0, 0.25); } 

    col *= pow(2.0 - abs(gluv_all.x), 0.2);

    // if ( abs(center.y) < mmv_rms_waveforms.x) {
    //     col += vec4(0.0, 0.0, 0.0, 0.4);
    // } 

    // if ( abs(center.y) < mmv_rms_waveforms.y) {
    //     col += mmv_alpha_composite(vec4(0.0, 0.7176, 1.0, 0.4), col);
    // } 


    fragColor = col;
}

