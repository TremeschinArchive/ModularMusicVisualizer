uniform float smooth_audio_amplitude;

struct Complex
{
    float x; float y;
    float r; float t;
};

Complex Complex2Polar(Complex a)
{
   a.r = sqrt(a.x*a.x + a.y*a.y);
   a.t = atan(a.y, a.x);
   return a;
}

Complex Complex2Cart(Complex a)
{
   a.x = a.r * cos(a.t);
   a.y = a.r * sin(a.t);
   return a;
}

Complex ComplexPower(Complex w, Complex z)
{
   Complex d;
   
   d.r = pow(w.r,z.x) * exp(-z.y * w.t);
   d.t = z.y * log(w.r) + z.x * w.t;
   d = Complex2Cart(d);

   return(d);
}

float ComplexLength(Complex n) {
    return sqrt(n.x*n.x + n.y*n.y);
}

void main()
{
    #pragma include coordinates_normalization;
    gluv *= 1.0 + 100.0 * ((smooth_audio_amplitude + smooth_audio_amplitude) / 2.0);
    vec3 col = vec3(0.0);
    
    Complex screen_point;
    screen_point.x = gluv.x;
    screen_point.y = gluv.y;
    screen_point = Complex2Polar(screen_point);
    
    Complex buffer;
    buffer = screen_point;
    
    int MAX_STEPS = 200;
    int iter = 0;
    
    for (int i = 0; i < MAX_STEPS; i++) {
        buffer = ComplexPower(screen_point, buffer);
        iter ++;
        float l = ComplexLength(buffer);
        //col = vec3(l);
        if (l > 40.0) {
            break;
        }
    }
    
    col = vec3(iter / MAX_STEPS, fract((iter / MAX_STEPS) * smooth_audio_amplitude), smooth_audio_amplitude);
    //col = vec3(screen_point.x);
    
    fragColor = vec4(col, 1.0);
}