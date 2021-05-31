from mmv.sombrero.sombrero_constructor import *
from mmv.sombrero.sombrero_shader import *

def generate(context):
    layers = []
    base = context.shaders_dir/"packs"/"base"

    # Background
    background = context.new_shader()
    background.macros.load(context.sombrero_dir/"glsl"/"menu.glsl")
    layers.append(background)

    # # Piano related

    pianoroll = context.create_piano_roll()
    pianoroll.synth.init(gain = 2)
    pianoroll.synth.set_audio_backend("pulseaudio")
    pianoroll.synth.load_sf2("/usr/share/soundfonts/FluidR3_GM.sf2")
    pianoroll.synth.fluid.set_reverb(roomsize = 1, damping = 0.9, width = 0.9, level = 1)
    pianoroll.load_midi(context.assets_dir/"Shyness of Liberty Midi.mid")

    # Midi keys
    pianomidi = context.new_shader()
    pianomidi.constructor = PianoRollConstructor(pianomidi, pianoroll, expect = "notes")
    pianomidi.macros.load(base/"piano_roll"/"midi_key.glsl")
    layers.append(pianomidi)

    # Piano keys
    pianokeys = context.new_shader()
    pianokeys.constructor = PianoRollConstructor(pianokeys, pianoroll, expect = "keys")
    pianokeys.macros.load(base/"piano_roll"/"piano_key.glsl")
    layers.append(pianokeys)
    
    context.render_layers(layers, gamma_correction = True, HUD = True)

