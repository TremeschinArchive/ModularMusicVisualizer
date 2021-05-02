#version 330
in vec2 in_pos;
in vec2 in_size;
out vec2 size;

void main() {
    // Position of the vertex on the screen
    gl_Position = vec4(in_pos, 0.0, 1.0);

    // Size that expands laterally
    size = in_size;
}