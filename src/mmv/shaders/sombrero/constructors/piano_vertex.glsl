#version 330
in vec2 in_pos;
in vec2 in_size;
in float in_note;
in float in_velocity;
in float in_channel;
in float in_is_playing;
in float in_is_white;

out vec2 size;
out float vert_note;
out float vert_velocity;
out float vert_channel;
out float vert_is_playing;
out float vert_is_white;

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