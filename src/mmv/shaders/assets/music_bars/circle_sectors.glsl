// uniform vec3 mmv_rms_0_33;

vec4 mainImage() {

    // Start with empty color (so it's fully transparent everywhere)
    vec4 col = vec4(0.0);
    vec3 mmv_rms_0_33 = vec3(0.0);
    vec3 mmv_progressive_rms = vec3(0.0);

    vec2 gluv_all = mGetGLUVAll(1.3);

    // // Movement

    // Movement offsets so bar isn't fixed on dead center
    float offset_speed = 0.3;
    float offset_amplitude = 0.102 * mmv_rms_0_33[2];

    // Offset vector 2 of x, y to add
    vec2 offset = vec2(
        sin(5.0 * mTime * offset_speed) * offset_amplitude,
        cos(8.0 * mTime * offset_speed) * offset_amplitude
    );

    // // Angles

    // Rotate the bars a bit
    float angle_offset = sin(mmv_progressive_rms[2] / 16.0)*0.16;

    // bars_uv is the offsetted coordinates which determines the center of the bars
    // gluv_all (0, 0) is center of screen so we offset that by the previous vector
    vec2 bars_uv = (gluv_all - offset);

    vec2 rotated_bars_uv = bars_uv * mRotation2D(angle_offset - PI/2);

    // Current angle we are to get the FFT values from
    float angle = mAtan2(rotated_bars_uv.y, rotated_bars_uv.x);

    // // Getting FFT

    // Circle sectors
    bool smooth_bars = false;
    float fft_val = 0.0;

    // Branch code if we want a smooth bars or rectangle-looking ones
    // mmv_radial_fft is a texture that starts on left channel low frequencies at x=0,
    // in x=0.5 we hit the left channel highest frequency and switch to the right channel ones
    // but this one is reversed, we start 0.5 high freq right channel and 1.0 is right channel 
    // lowest frequencies.

    // Proportion that given 0 is 0, 2pi is 1, angle is what?

    // We subtract from 2 because first channel is left and angle gets positive with
    // counter-clockwise rotation
    float proportion = 1.0 - mProportion(2 * PI, 1, angle);
    
    // FOR LINEAR FFT TODO: MAKE OWN FUNCTION
    // Mirror the angle after half since we have [[Low, High], [Low, High]] freqs of L/R channel
    // if (proportion > 0.5) {
    //     proportion = 1.0 - (proportion - 0.5);
    // }

    if (smooth_bars) {
        // Get the FFT val from the mmv_radial_fft texture with a float vec2 array itself.
        // GL will interpolate the texture for us into values in between, probably linear nearest
        fft_val = texture(mmv_fft, vec2(proportion, 0), 0).r;
    } else {
        // texelFetch accepts ivec2 (integer vec2)
        // which is the pixel itself, not filtered by GL
        fft_val = texelFetch(mmv_fft, ivec2(int(mmv_fft_resolution[0] * proportion), 0), 0).r;
    }

    // // Sizes, effect configuration

    // Radial "bloom"
    bool angelic = true;

    // Size of everybody, also scales bars
    float size = (0.13) + mmv_rms_0_33[2] * 0.133;

    // "Max" size of the music bar
    float bar_size = 0.4;

    // Size of the logo image relative to the music bars (ratio)
    float logo_relative_to_bar_ratio = 1.0 - (0.05 * smoothstep(mmv_rms_0_33[2], 0.0, 5.0));

    // // Render

    float barsize = size + ((fft_val/50.0) * bar_size);
    float away_from_center = length(bars_uv);

    // Distance from center is smaller than the FFT value times the bar size
    if (away_from_center < barsize) {
        // Set value of the bar color
        col = vec4(1.0 - fft_val / 50, 1.2, 1.0, 1.0);
    } else {
        // Angelic effect, we're not inside a bar and we add a white component
        // based on the distance we are, also have to account for bar size
        if (angelic) {
            col = vec4(1.0, 1.0, 1.0, 0.0) * 1.0;
            col.a = (size + (fft_val/20.0) * bar_size * bar_size) / pow(2.8 * away_from_center, 2.0);
        }
    }

    vec4 logo_pixel = vec4(0.0);

    // Get the logo, do some calculations
    logo_pixel = mBlitImage(
        col, logo,
        logo_resolution,
        bars_uv,
        vec2(0.0, 0.0), // anchor
        vec2(0.5, 0.5), // shift
        size * 2.0 * logo_relative_to_bar_ratio,  //scale
            sin(mTime*2.3 + mmv_progressive_rms[2]/8.0) / 8.0
            + sin(mTime*2.3 + mmv_progressive_rms[2]/5.0) / 8.0, //angle
        false, // repeat
        true, 2.0 // Undo gamma, Gamma
    );

    // Smooth edges on logo
    logo_pixel.a = smoothstep(size, size*0.95, length(bars_uv));

    // Alpha composite logo + bars
    col = mAlphaComposite(col, logo_pixel);

    // Return color
    return col;
}
