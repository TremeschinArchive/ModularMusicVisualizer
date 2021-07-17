#version 330
in vec2 InPos;
in vec2 InSize;
in float InNote;
in float InVelocity;
in float InChannel;
in float InIsPlaying;
in float InIsWhite;

out vec2 size;
out float Vertnote;
out float Vertvelocity;
out float Vertchannel;
out float VertIsPlaying;
out float VertIsWhite;

void main() {
    // Position of the vertex on the screen
    gl_Position = vec4(InPos, 0.0, 1.0);

    // Size that expands laterally
    size = InSize;
    Vertnote = InNote;
    Vertvelocity = InVelocity;
    Vertchannel = InChannel;
    VertIsPlaying = InIsPlaying;
    VertIsWhite = InIsWhite;
}