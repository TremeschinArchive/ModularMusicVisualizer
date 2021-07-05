#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

in vec2 size[];

out vec2 opengl_uv;
out vec2 shadertoy_uv;

void main() {
    vec2 center = gl_in[0].gl_Position.xy;
    vec2 hsize = size[0] / 2.0;

    // Top Left
    gl_Position = vec4(center + vec2(-hsize.x,  hsize.y), 0.0, 1.0);
    shadertoy_uv = vec2(0, 1);
    opengl_uv = vec2(-1, 1);
    EmitVertex();

    // Bottom Left
    gl_Position = vec4(center + vec2(-hsize.x, -hsize.y), 0.0, 1.0);
    shadertoy_uv = vec2(0, 0);
    opengl_uv = vec2(-1, -1);
    EmitVertex();

    // Top Right
    gl_Position = vec4(center + vec2( hsize.x,  hsize.y), 0.0, 1.0);
    shadertoy_uv = vec2(1, 1);
    opengl_uv = vec2(1, 1);
    EmitVertex();

    // Bottom Right
    gl_Position = vec4(center + vec2( hsize.x, -hsize.y), 0.0, 1.0);
    shadertoy_uv = vec2(1, 0);
    opengl_uv = vec2(1, -1);
    EmitVertex();
    
    EndPrimitive();
}