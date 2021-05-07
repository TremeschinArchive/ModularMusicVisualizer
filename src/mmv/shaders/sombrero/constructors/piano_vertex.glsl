#version 330
in vec2 in_pos;
in vec2 in_size;
in int in_note;
in int in_velocity;
in int in_channel;
in int in_is_playing;
in int in_is_white;

out vec2 size;
flat out int vert_note;
flat out int vert_velocity;
flat out int vert_channel;
flat out int vert_is_playing;
flat out int vert_is_white;

void main() {
    // Position of the vertex on the screen
    gl_Position = vec4(in_pos, 0.0, 1.0);

    // Size that expands laterally
    size = in_size;
    vert_note = in_note;
    vert_velocity = in_velocity;
    vert_channel = in_channel;
    vert_is_playing = in_is_playing;
    vert_is_white = in_is_white;
}