"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaPianoRollVectorial object for MIDI visualization

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

from mmv.mmvskia.piano_rolls.mmv_piano_roll_top_down import MMVSkiaPianoRollTopDown
from mmv.common.cmn_midi import MidiFile
from mmv.common.cmn_utils import Utils


class MMVSkiaPianoRollVectorial:
    """
    kwargs:
    {
        "bpm": BPM of the midi file set in Context.input_midi
        "type": str, "top-down", determines what class of PianoRoll to use
            "top-down": MMVSkiaPianoRollTopDown

        For MMVSkiaPianoRollTopDown:
            {
                "color_preset": string, "default"
                    Colors preset filename under this file directory, subdirectory colors
                    Don't send with ".yaml", it auto adds it
                "do_draw_markers": bool, True
                    Draw orientation markers, lines in between keys?
                "bleed": int, 3
                    Extra keys rendered counting down and up from the min and max key for clarity
                "seconds_of_midi_content": int, 3
                    Seconds of midi note "content" on screen, time for them to cross the screen
                "seconds_offset": float, 0
                    If your MIDI file is not synced with the audio, we delay the keys on screen by this amount
            }
    
    }
    """
    def __init__(self, mmv, **kwargs) -> None:
        
        debug_prefix = "[MMVSkiaPianoRollVectorial.__init__]"

        self.mmv = mmv
        self.config = {}

        self.utils = Utils()

        self.is_deletable = False
        self.offset = [0, 0]

        # # General configuration

        self.config["bpm"] = kwargs["bpm"]
        self.config["type"] = kwargs.get("type", "top-down")

        # MMVSkiaPianoRollTopDown
        if self.config["type"] == "top-down":
            self.config["color_preset"] = kwargs.get("color_preset", "default")
            self.config["do_draw_markers"] = kwargs.get("do_draw_markers", True)
            self.config["bleed"] = kwargs.get("bleed", 3)
            self.config["seconds_of_midi_content"] = kwargs.get("seconds_of_midi_content", 3)
            self.config["seconds_offset"] = kwargs.get("seconds_offset", 0)

        else:
            raise RuntimeError("No matching MMVSkiaPianoRollVectorial type, kwargs:", kwargs)

        # # Load MIDI file, get timestamps

        print(debug_prefix, "Loading the MIDI file")
        self.midi = MidiFile()
        self.midi.load(self.mmv.context.input_midi, bpm = self.config["bpm"])
        
        print(debug_prefix, "Getting notes timestamps")
        self.midi.get_timestamps()

        # We have different files with different classes of PianoRolls

        # Simple, rectangle bar
        if self.config["type"] == "top-down":
            print(debug_prefix, "Piano roll class is MMVSkiaPianoRollTopDown")
            self.builder = MMVSkiaPianoRollTopDown(self.mmv, self)

        print(debug_prefix, "Generating Piano Roll")
        self.builder.generate_piano(self.midi.range_notes.min, self.midi.range_notes.max)

    # Call builder for drawing directly on the canvas
    def next(self, effects):
        self.builder.build(effects)
