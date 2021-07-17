#version 330
in vec2 InPos;
in vec2 InSize;
out vec2 size;

void main() {
    // Position of the vertex on the screen
    gl_Position = vec4(InPos, 0.0, 1.0);

    // Size that expands laterally
    size = InSize;
}