

// ===============================================================================

uniform float smooth_audio_amplitude;
uniform float smooth_audio_amplitude2;
uniform float progressive_amplitude;
uniform vec3 standard_deviations;
uniform vec3 average_amplitudes;

#pragma include mmv_specification once

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple

    vec3 col = vec3(0.0);
    int n = 90;
    
    float r_time = progressive_amplitude * 0.08;

    for (int index = 0; index < n; index ++) {
        float tanx =  r_time + mmv_time * (0.8 + 0.2 * rand(float(index))) + rand(float(index) + 0.022) * PI;
        float r = tan(mod(tanx, PI/2.0));
        float angle = 
            fract(
                rand(float(index) + 0.58 + 0.2*int(tanx / (PI/2.0)))
            ) * 2.0 * PI
            + 0.08 * sin(6.0 * mmv_time * (0.6 + 0.2*rand(float(index))));
        
        col += (1.0 / length(gluv - vec2(r*cos(angle), r*sin(angle)))) * 0.0022 * (1 / (length(gluv) + 0.3));
    }
    
    
    fragColor = vec4(col, col.r);
}
