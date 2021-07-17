#version 330
layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

in vec2 size[];

// Piano
in float Vertnote[];
in float Vertvelocity[];
in float Vertchannel[];
in float VertIsPlaying[];
in float VertIsWhite[];

out float note;
out float velocity;
out float channel;
out float IsPlaying;
out float IsWhite;

// Coords
out vec2 OpenGLUV;
out vec2 ShaderToyUV;

void main() {
    vec2 center = gl_in[0].gl_Position.xy;
    vec2 hsize = size[0] / 2.0;

    note = Vertnote[0];
    velocity = Vertvelocity[0];
    channel = Vertchannel[0];
    IsPlaying = VertIsPlaying[0];
    IsWhite = VertIsWhite[0];

    // Top Left
    gl_Position = vec4(center + vec2(-hsize.x,  hsize.y), 0.0, 1.0);
    ShaderToyUV = vec2(0, 1);
    OpenGLUV = vec2(-1, 1);
    EmitVertex();

    // Bottom Left
    gl_Position = vec4(center + vec2(-hsize.x, -hsize.y), 0.0, 1.0);
    ShaderToyUV = vec2(0, 0);
    OpenGLUV = vec2(-1, -1);
    EmitVertex();

    // Top Right
    gl_Position = vec4(center + vec2( hsize.x,  hsize.y), 0.0, 1.0);
    ShaderToyUV = vec2(1, 1);
    OpenGLUV = vec2(1, 1);
    EmitVertex();

    // Bottom Right
    gl_Position = vec4(center + vec2( hsize.x, -hsize.y), 0.0, 1.0);
    ShaderToyUV = vec2(1, 0);
    OpenGLUV = vec2(1, -1);
    EmitVertex();
    
    EndPrimitive();
}