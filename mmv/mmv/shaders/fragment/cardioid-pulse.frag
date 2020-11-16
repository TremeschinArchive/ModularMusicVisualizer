#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform float u_time;

void main() {
    vec2 screen = gl_FragCoord.xy/u_resolution.xy; 
    float zoom = 3.0;
    
    screen = zoom * (screen - 0.5);
    screen.y = screen.y - 0.5;
    screen.x *= u_resolution.x/u_resolution.y;

    vec3 color = vec3(0.);
    float theta = 0.0;
    
    if (screen.x > 0.0) {
    	theta = atan(screen.y / screen.x);
    } else {
        theta = atan(-screen.y / screen.x);
    }
    
    float r = pow(pow(screen.x, 2.0) + pow(screen.y, 2.0), 0.5);
    
    float fx1 = (1.0 - sin(theta))/2.0;
    float fx2 = (-0.5 + 2.0*cos(theta))/2.0;
    
    float distance1 = abs(fx1 - r);
    float distance2 = abs(fx2 - r);
    
    color.r = distance1 + abs(sin(u_time));
    color.g = pow(distance1, abs(sin(2.0 * u_time)));
    color.b = pow(distance2 + distance1, cos(sin(3.0 * u_time)));

    gl_FragColor = vec4(color, 1.0);
}
