
// Tetration fractal

// Please include complex.glsl

vec4 mainImage(in vec2 fragCoord) {
    vec4 col = vec4(0.0);
    vec2 gluv = mGetGLUVAll();
    
    // This point
    ComplexNumber screen_point;

    screen_point.x = gluv.x;
    screen_point.y = gluv.y;
    screen_point = ComplexNumber2Polar(screen_point);
    
    ComplexNumber temporary;
    temporary = screen_point;
    
    int MAX_STEPS = 50;// int(200 * (0.5 - 0.5*sin(2*PI * mTime / 180.0)));
    int iter = 0;
    
    for (int i = 0; i < MAX_STEPS; i++) {
        temporary = ComplexNumberPower(screen_point, temporary);
        iter ++;
        float l = ComplexNumberLength(temporary);
        
        //col = vec3(l);
        if (l > 40.0) {break;}
    }
    
    // col = vec4(iter / MAX_STEPS, fract((iter / MAX_STEPS)), 0.0, 1.0);
    float k = iter / MAX_STEPS;
    col = vec4(k, k, k, 1.0);
    //col = vec3(screen_point.x);
    return col;    
}