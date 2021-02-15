

// ===============================================================================

#pragma map name music_bars_particle

#pragma include mmv_specification once

void main() {
    #pragma include coordinates_normalization multiple
    #pragma include math_constants multiple

    // How many particles
    int n = 40;
    
    // Radius over time
    float r_time = progressive_amplitude * 0.08;

    // Particle color and starting alpha
    vec3 parcol = vec3(0.0);
    float alpha = 0.0;

    for (int index = 0; index < n; index ++) {
        float baserandom = rand(float(index));

        // The X we calculate tan(x) for getting the radius this particle is at
        float tanx = 
            
            // "Radius over time"
            r_time 
            
            // Base random on time
            + mmv_time * (0.3 + 1.5 * baserandom)

            // And some more randomness but baserandom
            + rand(float(index) + 0.022) * PI;

        // Radius is some tan(mod(x, pi/2)) raised to some power to control speed
        float r = pow(mod(tanx, PI/2.0), 2.0);

        // Angle this particle is at
        float angle = 
        
            // Unique ind -> same angle
            fract(
                rand(float(index) + 0.58 + 0.2*int(tanx / (PI/2.0)))
            ) * 2.0 * PI

            // Variation of angle through time, low sine amplitude
            + 0.02 * sin(
                6.0 * mmv_time * (0.6 + 0.2 * baserandom)
            )
            
            // More audio lately = more angle shake / variation, gives more organic movement
            + sin(progressive_amplitude * 4.0) * 0.01

            // More audio lately = more general angle, yet other more organic movement
            + 0.02 * sin(baserandom * mmv_time/4.0) * progressive_amplitude / 8.0;
        
        // Base luminosity on audio amplitude, also avoid division by zero and yes this can be
        // merged with the other one at the bottom where we calculate the alpha
        float luminosity = (0.0022 * (1 / (length(gluv) + 0.3))) + (smooth_audio_amplitude * 0.0002);

        // Actual distance
        float l = length(gluv - vec2(r*cos(angle), r*sin(angle)));

        // Alpha value for alpha compositing, max of each particle index and this other new one
        // with different ratios of pow() so we have different base luminosity
        alpha = max((1.0 / pow(l, 0.8 + 0.3 * baserandom)) * luminosity, alpha);

        // Start transparent at center, grows to opaque
        alpha *= smoothstep(length(gluv), 0.0, 0.05);
        // parcol = vec3(baserandom, 1.0, 1.0 - baserandom);
        parcol = vec3(1.0);
    }
    
    // Output fragment color
    fragColor = vec4(parcol, alpha);
}
