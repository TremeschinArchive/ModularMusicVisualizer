

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

    float alpha = 0.0;
    int n = 80;
    
    float r_time = progressive_amplitude * 0.08;

    for (int index = 0; index < n; index ++) {
        float tanx = r_time + mmv_time * (0.3 + 1.5 * rand(float(index))) + rand(float(index) + 0.022) * PI;
        float r = pow(mod(tanx, PI/2.0), 3.0);
        float angle = 
            fract(
                rand(float(index) + 0.58 + 0.2*int(tanx / (PI/2.0)))
            ) * 2.0 * PI
            + 0.08 * sin(6.0 * mmv_time * (0.6 + 0.2*rand(float(index)))
        );
        
        float luminosity = (0.0022 * (1 / (length(gluv) + 0.3))) + (smooth_audio_amplitude * 0.0002);
        float l = length(gluv - vec2(r*cos(angle), r*sin(angle)));
        alpha = max((1.0 / (l)) * luminosity, alpha);
    }
    
    fragColor = vec4(vec3(1.0), alpha);
}
