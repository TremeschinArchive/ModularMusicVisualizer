"""
===============================================================================

Purpose: MIDI file utilities for reading, organizing, sorting information

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

from mmv.common.cmn_utils import DataUtils
from midi2audio import FluidSynth
import mido
import copy


# Store the range of notes for a (possible) piano roll visualization if user
# choses only to show range of played keys, helps visualization on smaller screens
class RangeNotes:
    def __init__(self):
        self.min = -1
        self.max = -1
    
    # Update min and max variables based on a new note index
    def update(self, new_note):
        # First call, set max and min to incoming note
        if self.min == -1 and self.max == -1:
            self.max = new_note
            self.min = new_note
            return
        # Check if eiter is below or above, update corresponding variable
        if self.max < new_note:
            self.max = new_note
        if new_note < self.min:
            self.min = new_note


# Wrapper and utilities for mido interface, processing MIDI files.
class MidiFile:
    def load(self, path, bpm=130):
        self.midi = mido.MidiFile(path, clip=True)
        self.tempo = mido.bpm2tempo(bpm)
        self.range_notes = RangeNotes()
        self.datautils = DataUtils()
        self.path = path
    
    # Midi note index (number) to name -> "C3", "A#4", F5, etc
    def note_to_name(self, n):
        # 69 -> A4
        # 60 -> C4
        letters = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = str((n // 12) - 1)
        letter = letters[(n + 60) % 12]
        return letter + octave

    # Basically, MIDI information -> timestamps dictionary
    # Really finicky because how MIDI works on the ticks and channels and whatnot
    def get_timestamps(self):
        debug_prefix = "[MidiFile.get_timestamps]"

        self.time_first_note = None
        self.time = 0

        # Empty channels dictionary list
        channels = { channel: {} for channel in range(0, 16) }

        # Timestamps dictionary and "ongoing" midi notes, not finished        
        self.timestamps = {
            **{"tempo": []},
            **channels,
        }

        ongoing = copy.deepcopy(channels)

        self.used_channels = []

        # Iterate through each message on ALL midi tracks together...
        # Use synchronous mode if possible TODO: right loop for every mode
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

                # Time that the first note plays
                if self.time_first_note is None:
                    print(debug_prefix, f"Time of the first playing note on the MIDI file = [{self.time}]")
                    self.time_first_note = self.time
                
                velocity = msg.velocity
                channel = msg.channel
                note = msg.note

                if not channel in self.used_channels:
                    self.used_channels.append(channel)

                self.range_notes.update(note)

                if note in ongoing[channel].keys():

                    if not note in self.timestamps[channel].keys():
                        self.timestamps[channel][note] = {"time": []}

                    # Append start, end and info values as a list
                    self.timestamps[channel][note]["time"].append([
                        ongoing[channel][note]["start"],
                        self.time,
                        {
                            "velocity": velocity
                        }
                    ])

                    del ongoing[channel][note]
                else:
                    ongoing[channel][note] = {
                        "start": self.time,
                    }
                
            if msg.type == 'set_tempo':
                self.tempo = msg.tempo
                self.timestamps["tempo"].append([
                    self.time, self.tempo
                ])
        self.used_channels.sort()

        print("Channels on midi file:", self.used_channels)

        # TODO: Need to adapt function to accept {} as third argument   
        # for key in self.timestamps.keys():
        #     if isinstance(key, int):
        #         self.timestamps[key]["time"] = self.datautils.shorten_overlaps_keep_start_value(self.timestamps[key]["time"])
       
        # print(self.timestamps)
        # print("Range:", self.range_notes.min, self.range_notes.max)
        # print(self.timestamps)
    
    # Uses midi2audio for converting the input midi file
    def convert_to_audio(self, save_path, sample_rate = 44000):
        print(f"[MidiFile.convert_to_audio] Converting [{self.path}] -> [{save_path}] @{sample_rate}Hz")
        fs = FluidSynth(sample_rate = sample_rate)
        fs.midi_to_audio(self.path, save_path)
        return save_path