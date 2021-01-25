void main() {
    fragColor = vec4(shadertoy_uv.x, shadertoy_uv.y, abs(sin(mmv_time)), 1.0);
}   
