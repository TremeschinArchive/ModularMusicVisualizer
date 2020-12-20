//!TEXTURE LOGO
//!SIZE <+IMAGEWIDTH+> <+IMAGEHEIGHT+>
//!FORMAT rgba8
//!FILTER NEAREST
//!BORDER REPEAT
<+IMAGEHEX+>


//!HOOK SCALED
//!BIND HOOKED
//!DESC fit-multiple
//!BIND LOGO
vec4 hook() {
    vec4 video_texture = HOOKED_tex(HOOKED_pos);
    vec4 texture = texture(LOGO, HOOKED_pos + vec2(0.5, 0.5));

    float blend = 0.2;

    video_texture = ((1.0 - blend) * video_texture) + (blend * texture);
  
    return video_texture;
} 
