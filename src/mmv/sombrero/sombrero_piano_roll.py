"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Piano roll and midi file processor

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""
from intervaltree import IntervalTree
from intervaltree import Interval
from functools import cache
import fluidsynth
import logging
import imgui
import mido
import math


def midi_index_to_name(note):
    return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][(note + 60) % 12] + str((note // 12) - 1)

@cache
def is_white_key(note): return "#" in midi_index_to_name(note)

# Attributes one Midi Note will have, the usual: which, when, how much, where
class MidiNote:
    def __init__(self, note, start, end, channel = 0, velocity = 100, transpose = 0):
        self._note = note
        self.start = start
        self.end = end
        self.channel = channel
        self.velocity = velocity  
        self.transpose = transpose

    @property # Name given by offset of 60 that repeats every octave (12 notes), and the octave we are. [69 -> A4], [60 -> C4]
    def name(self): return midi_index_to_name(self.note)

    @property
    def note(self): return self._note + self.transpose

    # Pretty string representation of the note just in case we need it
    def __repr__(self): return f"[Note |{self.name.ljust(3)}| (ch={self.channel}, vel={self.velocity}) ({self.start:.2f}:{self.end:.2f})"
 

class MidiFile:
    def load(self, path, bpm = 130):
        self.midi_file_path = path
        self.midi = mido.MidiFile(path, clip = True)
        self.tempo = mido.bpm2tempo(bpm)
        self.time = 0
        self.transpose = 0

        # Min and max notes played
        self.min, self.max = math.inf, -math.inf

        # Notes being played (now)
        ongoing = {}

        # Iterate through each message on ALL midi tracks together...
        for msg in mido.merge_tracks(self.midi.tracks):
           
            # Convert message time from absolute time
            # in ticks to relative time in seconds.
            if msg.time > 0:
                delta = mido.tick2second(msg.time, self.midi.ticks_per_beat, self.tempo)
            else:
                delta = 0
            
            # Add to current time the delta based on tempo
            self.time += delta

            # Message is a note we play or release (or weirdly play at zero velocity for releasing)
            if msg.type in ["note_on", "note_off"]:
                velocity = msg.velocity
                channel = msg.channel
                note = msg.note

                # Empty dictionary for ongoing channel
                if not channel in ongoing: ongoing[channel] = {}

                # Note ended
                if note in ongoing[channel].keys():
                    d = ongoing[channel][note]
                    
                    # Update min and max ranges of notes
                    if note > self.max: self.max = note
                    if note < self.min: self.min = note

                    # Yield midi note
                    yield MidiNote(note = note, start = d["start"], end = self.time, channel = channel, velocity = d["velocity"])

                    del ongoing[channel][note]
                
                else: # New note
                    ongoing[channel][note] = {"start": self.time, "velocity": velocity}
            
            # Set new tempo
            if msg.type == 'set_tempo': self.tempo = msg.tempo
        
        # Bleeding
        self.max += 2
        self.min -= 2

    # Converts this midi file set previously to audio
    def convert_to_audio(self, source_path, save_path, musescore_binary, bitrate = 300000):
        debug_prefix = "[MidiFile.convert_to_audio]"
        print(f"{debug_prefix} Converting [{source_path}] -> [{save_path}]")
        
        # If there is already a file by the save_path name, don't convert
        if os.path.exists(save_path):
            print(f"{debug_prefix} Save path [{save_path}] already exists, not converting to audio and overwriting..")
            return

        # Command for converting midi -> audio
        command = [
            musescore_binary,
            "-i", source_path,
            "-o", save_path,
            "-b", str(bitrate),  
        ]

        # Log for debug and info
        print(f"{debug_prefix} Command to run for converting midi to audio: {command}")
        print(f"{debug_prefix} This might take a while, be patient..")

        # Don't try opening gui on headless ?
        env = os.environ.copy()
        if False:  # FIXME: workaround?
            env["QT_QPA_PLATFORM"] = "offscreen"
        
        # Run command
        subprocess.check_output(command, env = env)

        # Assert we were successful?
        if not os.path.exists(save_path):
            print(f"{debug_prefix} Target save path don't exist after converting to audio [{save_path}]")
            sys.exit(-1)

        # Return
        return save_path


class FluidSynthUtils:
    def init(self, gain): self.fluid = fluidsynth.Synth(gain = 1)
    def reset(self):
        for channel in range(0, 16):
            for note in range(0, 128):
                self.key_up(note, channel)
        self.fluid.delete()
    def set_audio_backend(self, audio_backend): self.fluid.start(driver = audio_backend)
    def load_sf2(self, path): self.soundfont = self.fluid.sfload(path); self.select(0, 0, 0)
    def select(self, channel, bank, preset): self.fluid.program_select(channel, self.soundfont, bank, preset)
    def key_down(self, note, velocity, channel = 0): self.fluid.noteon(channel, note, velocity)
    def key_up(self, note, channel = 0): self.fluid.noteoff(channel, note)


class PianoRoll:
    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl
        self.context = self.sombrero_mgl.context
        self.__scene_contents = {}
        self.__playing_notes_fluid = []

        # Midi file wrapper
        self.midi = MidiFile()
        self.synth = FluidSynthUtils()

        # Add user pressed keys and midi file contents
        for name in ["user", "midi"]: self.__reset_scene_content(name)

        # How much seconds of content on screen
        self.visible_seconds = 5
        self.time_draw_bleed = self.visible_seconds * 0.5
        self.piano_height = 0.3
        self.transpose = 0

        # Optimization
        self.__last_call_generate_coordinates = None

    def gui(self):
        imgui.separator()
        imgui.text_colored("Piano Roll", 0, 1, 0)
        changed, value = imgui.slider_float("Piano Height", self.piano_height, min_value = 0, max_value = 1, power = 1)
        if changed: self.piano_height = value
        changed, value = imgui.slider_float("Seconds of Notes", self.visible_seconds, min_value = 0.1, max_value = 8, power = 1)
        if changed: self.visible_seconds = value
        
        # # Min note
        changed, value = imgui.slider_int("Min Note", self.midi.min, min_value = -2, max_value = self.midi.max - 1)
        if changed: self.midi.min = value; 

        # # Max note
        changed, value = imgui.slider_int("Max Note", self.midi.max, min_value = self.midi.min + 1, max_value = 130)
        if changed: self.midi.max = value

        changed, value = imgui.slider_int("Transpose", self.transpose, min_value = -48, max_value = 48)
        if changed:
            self.__playing_notes_fluid = []
            self.transpose = value
            for note in self.get_playing_notes_in_range(0, math.inf):
                note.transpose = value
            
        imgui.separator()

    # # Internal functions

    # Add interval trees into contents dictionary for every note possible on MIDI files
    def __reset_scene_content(self, name): self.__scene_contents[name] = {index: IntervalTree() for index in range(0, 128)}

    # Scene must exist to do something..?
    def __assert_scene_exists(self, scene):
        assert scene in self.__scene_contents.keys(), f"Scene [{scene}] doesn't exist [{list(self.__scene_contents.keys())}]"

    # Geneator for every key indexes and their intervals on self.__scene_contents
    def __every_key_interval(self) -> Interval:

        # Iterate on scenes (user and midi files)
        for scene in self.__scene_contents.values():

            # For each interval in the items (key indexes), add to the notes list every data
            # on the interval that matches the start and end search arguments of this function
            for interval in scene.values():
                yield interval
    
    # # User functions

    # Add MidiNote class to a interval in the contents.
    # "note" can be of type MidiNote
    def add_note(self, note, start = 0, end = 0, channel = 0, velocity = 100, scene = "midi") -> None:
        if note.start == note.end: return
        self.__assert_scene_exists(scene)

        # We were given a MidiNote class
        if isinstance(note, MidiNote):
            self.__scene_contents[scene][note.note][note.start:note.end] = note
        
        else: # From raw values
            midi_note = MidiNote(note = note, start = start, end = end, channel = channel, velocity = velocity)
            self.__scene_contents[scene][note][start:end] = midi_note

    # Write midi keys from a midi file as MidiNotes here
    def load_midi(self, path):
        for note in self.midi.load(path):
            self.add_note(note)

    # Notes playing in some range
    def get_playing_notes_in_range(self, start, end) -> list:
        return [content.data for interval in self.__every_key_interval() for content in interval[start:end]]

    # Notes being played at specific time
    def get_playing_notes_at(self, time) -> list:
        return [content.data for interval in self.__every_key_interval() for content in interval[time]]
    
    # Notes visible
    def get_visible_notes(self):
        return self.get_playing_notes_in_range(
            start = self.now - self.time_draw_bleed, end = self.now + self.visible_seconds + self.time_draw_bleed)

    @property
    def now(self): return self.sombrero_mgl.pipeline["mTime"]
    
    # Notes being played right now 
    def get_playing_now(self): return self.get_playing_notes_at(time = self.now)

    # Linear interpolation
    def lerp(self, p1, p2, x): return ((p2[1] - p1[1]) / (p2[0] - p1[0]))*(x - p2[0]) + p2[1]

    def generate_note_coordinates(self):
        if self.now == self.__last_call_generate_coordinates:
            return self.__last_return_generate_note_coordinates

        self.__last_call_generate_coordinates = self.now

        playing = self.get_visible_notes()
        playing_now = self.get_playing_now()

        # # Play notes

        todel = []
        for index, note in enumerate(self.__playing_notes_fluid):
            if (not note in playing_now):
                self.synth.key_up(note.note)#, note.channel)
                todel.append(index)

        for index in reversed(todel): del self.__playing_notes_fluid[index]

        if self.context.freezed_pipeline:
            for note in self.__playing_notes_fluid:
                self.synth.key_up(note.note)#, note.channel)
                self.__playing_notes_fluid = []
        else:
            for note in playing_now:
                if (not note in self.__playing_notes_fluid):
                    self.__playing_notes_fluid.append(note)
                    self.synth.key_down(note.note, note.velocity)#, note.channel)
                    print("Kew down", note)
        
        # # Process

        instructions = {"notes": [], "keys": []}
        width = (2) / (self.midi.max - self.midi.min)
        S = 2

        for note in range(self.midi.min, self.midi.max + 1):
            x = self.lerp((self.midi.min, -1), (self.midi.max, 1), note)

            # # Piano key
            this_instruction = []

            # Coordinates
            this_instruction += [x, (-1 + self.piano_height / 2), S*width, S*self.piano_height]
            is_playing = any([note == playing.note for playing in playing_now])
            this_instruction += [note, 0, 0, is_playing, not "#" in midi_index_to_name(note)]
            instructions["keys"].append(this_instruction)

        for note in playing:
            this_instruction = []
            lower_boundary = -1 + self.piano_height

            # Get note X position
            x = self.lerp((self.midi.min, -1), (self.midi.max, 1), note.note)

            # Visible stuff
            viewport = ((self.now, lower_boundary), (self.now + self.visible_seconds, 1))

            # Start, end
            start = self.lerp(*viewport, note.start - self.now)
            end = self.lerp(*viewport, note.end - self.now)

            # Width, Height
            height = end - start

            # Y pos
            y = self.lerp(
                (0, lower_boundary), (self.visible_seconds, 1),
                note.end - self.now
            )

            # If note is playing now
            is_playing = any([note.note == playing.note for playing in playing_now])

            # Attributes
            note_attrs = [note.note, note.velocity, note.channel, int(is_playing), int(not "#" in note.name)]

            # Midi coordinate and attributes
            this_instruction += [x, y - height/2, S*width, S*height] + note_attrs
            instructions["notes"].append(this_instruction)

        self.__last_return_generate_note_coordinates = instructions
        return instructions


# # # # # # # # # # # # # # # Testing



if __name__ == "__main__":
    import itertools
    import random
    import time

    class Dummy:
        def __init__(self):
            self.visible_seconds = 3

    p = MMVShaderPianoRoll(Dummy())

    # test = "intervals"
    # test = "speed"
    test = "midi"

    if test == "midi":
        p.load_midi("contingency_times.mid")
        
        print("Playing at 2 seconds:")
        for n in p.get_playing_notes_at(2):
            print(f" :: {n}")

    if test == "speed":
        for _ in range(500000):
            s = random.uniform(0, 10000)
            p.add_note(random.randint(0, 127), s, s + random.uniform(0, 4))

        start = time.time()

        for i in itertools.count():
            k = p._get_playing_notes_in_range(4000, 4005)
            if i % 100 == 0:
                print(i / (time.time() - start), len(k))

    elif test == "intervals":

        p.add_note(10, 1, 2); p.add_note(12, 1.5, 2.5); p.add_note(17, 2.5, 3); p.add_note(13, 3.1, 3.5)

        print("\nPlaying at 1.6")
        for k in p.get_playing_notes_at(1.6):
            print(f" :: {k}")

        print("\nPlaying between 1.5, 3")
        for k in p.get_playing_notes_in_range(1.5, 3):
            print(f" :: {k}")
