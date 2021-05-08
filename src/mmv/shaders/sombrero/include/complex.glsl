
// Code adapted from http://paulbourke.net/fractals/tetration
//
// - http://paulbourke.net/fractals/tetration/tetrationlibrary.h
// - http://paulbourke.net/fractals/tetration/tetrationlibrary.c
//
// Credits to the original author, I, Tremeschin, adapted from C to GLSL

// x, y rectangular coords
// r, t polar coords
struct ComplexNumber {
    float x, y;
    float r, t;
};

// Returns the number itself, used for self-updating manually the polar
// coords components from this number as that isn't done automatically
ComplexNumber ComplexNumber2Polar(ComplexNumber n) {
   n.r = sqrt(n.x*n.x + n.y*n.y);
   n.t = atan(n.y, n.x);
   return n;
}

// Same idea as 2Polar but here we, from current polar points, yield
// or more like yield the same number, update the cartesian coords
ComplexNumber ComplexNumber2Cart(ComplexNumber n) {
   n.x = n.r * cos(n.t);
   n.y = n.r * sin(n.t);
   return n;
}

// Complex number power, it just works don't ask me why
ComplexNumber ComplexNumberPower(ComplexNumber w, ComplexNumber z) {
   ComplexNumber d;
   d.r = pow(w.r,z.x) * exp(-z.y * w.t);
   d.t = z.y * log(w.r) + z.x * w.t;
   d = ComplexNumber2Cart(d);
   return(d);
}

// Magnitude of complelx number, be sure to update the rectangular coords
// Yes, we could just return r as well...
float ComplexNumberLength(ComplexNumber n) {
    return sqrt(n.x*n.x + n.y*n.y);
}
