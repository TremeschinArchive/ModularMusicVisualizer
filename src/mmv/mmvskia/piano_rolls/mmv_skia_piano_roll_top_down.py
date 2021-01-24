"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaPianoRollTopDown object

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

from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_utils import DataUtils
from PIL import ImageColor
import numpy as np
import random
import math
import skia
import os


class MMVSkiaPianoRollTopDown:
    def __init__(self, mmv, MMVSkiaPianoRollVectorial):
        self.mmvskia_main = mmv
        self.vectorial = MMVSkiaPianoRollVectorial
        self.config = self.vectorial.config
        self.functions = Functions()
        self.datautils = DataUtils()
        self.piano_keys = {}
        self.keys_centers = {}
        self.colors = {}

        # Generate skia.Color4F out of the colors dictionary
        self.colors = self.parse_colors_dict(colors_dict = self.config["colors"])

        self.font_fits_on_width = {}

    # Recursively parse a colors dict
    def parse_colors_dict(self, colors_dict):
        for key, value in colors_dict.items():
            if value is None:
                colors_dict[key] = None
                continue 
            
            if isinstance(value, dict):
                colors_dict[key] = self.parse_colors_dict(colors_dict = value)
                continue

            if isinstance(value[0], int):
                value = [v / 256 for v in value]

            colors_dict[key] = skia.Color4f(*value)
        return colors_dict

    # Bleed is extra keys you put at the lower most and upper most ranged keys
    def generate_piano(self, min_note, max_note):

        debug_prefix = "[MMVSkiaPianoRollTopDown.generate_piano]"

        # NOTE: EDIT HERE STATIC VARIABLES  TODO: set them on config
        self.piano_height = (3.5/19) * self.mmvskia_main.context.height
        self.viewport_height = self.mmvskia_main.context.height - self.piano_height

        # Pretty print
        print("Add key by index: {", end = "", flush = True)

        # For each key index, with a bleed (extra keys) counting up and down from the minimum / maximum key index
        for key_index in range(min_note - self.config["bleed"], max_note + self.config["bleed"]):

            # Create a PianoKey object and set its index
            next_key = PianoKey(self.mmvskia_main, self.vectorial, self)
            next_key.by_key_index(key_index)

            # Pretty print
            if not key_index == max_note + self.config["bleed"] - 1:
                print(", ", end = "", flush = True)
            else:
                print("}")

            # Add to the piano keys list
            self.piano_keys[key_index] = next_key

        print(debug_prefix, "There will be", len(self.piano_keys.keys()), "keys in the piano roll")
        
        # We get the center of keys based on the "distance walked" in between intervals
        # As black keys are in between two white keys, we walk half white key width on those
        # and a full white key between E and F, B and C.

        # Get number of semitones (divisions) so we can calculate the semitone width afterwards
        divisions = 0

        # For each index and key index (you'll se in a while why)
        for index, key_index in enumerate(self.piano_keys.keys()):

            # Get this key object
            key = self.piano_keys[key_index]
            
            # First index of key can't compare to previous key, starts at current_center
            if not index == 0:

                # The previous key can be a white or black key, but there isn't a previous at index=0
                prevkey = self.piano_keys[key_index - 1]

                # Both are True, add two, one is True, add one
                # 2 is a tone distance
                # 1 is a semitone distance
                # [True is 1 in Python]
                divisions += (prevkey.is_white) + (key.is_white)

        # The keys intervals for walking
        self.semitone_width = self.mmvskia_main.context.width / divisions
        self.tone_width = self.semitone_width * 2

        self.set_best_font()

        # Current center we're at on the X axis so we send to the keys their positions
        current_center = 0

        # Same loop, ignore index=0
        for index, key_index in enumerate(self.piano_keys.keys()):

            # Get this key object
            key = self.piano_keys[key_index]
            
            # First index of key can't compare to previous key, starts at current_center
            if not index == 0:

                prevkey = self.piano_keys[key_index - 1]

                # Distance is a tone
                if (prevkey.is_white) and (key.is_white):
                    current_center += self.tone_width

                # Distance is a semitone
                else:
                    current_center += self.semitone_width

            # Set the note length according to if it's white or black
            if key.is_white:
                this_note_width = self.tone_width
            else:
                this_note_width = (4/6) * self.tone_width

            # Set attributes to this note we're looping
            self.piano_keys[key_index].width = this_note_width
            self.piano_keys[key_index].height = self.piano_height
            self.piano_keys[key_index].resolution_height = self.mmvskia_main.context.height
            self.piano_keys[key_index].center_x = current_center

            # And add to the key centers list this key center_x
            self.keys_centers[key_index] = current_center

    # Draw the piano, first draw the white then the black otherwise we have overlaps
    def draw_piano(self):
        
        end_piano_pos = self.mmvskia_main.context.height - self.piano_height
        screen_coords = [-200, end_piano_pos, self.mmvskia_main.context.width + 200, end_piano_pos]

        # Make the skia Paint and
        screen_paint = skia.Paint(
            AntiAlias = True,
            Style = skia.Paint.kStroke_Style,
            ImageFilter = skia.ImageFilters.DropShadowOnly(0, 0, 12, 12, self.colors["end_piano_shadow"]),
            StrokeWidth = 20
        )

        self.mmvskia_main.skia.canvas.drawRect(skia.Rect(*screen_coords), screen_paint)

        # White keys
        for key_index in self.piano_keys.keys():
            if self.piano_keys[key_index].is_white:
                self.piano_keys[key_index].draw(self.notes_playing)

        # Black keys
        for key_index in self.piano_keys.keys():
            if self.piano_keys[key_index].is_black:
                self.piano_keys[key_index].draw(self.notes_playing)
        

    # Draw the markers IN BETWEEN TWO WHITE KEYS
    def draw_markers(self):

        # The paint of markers in between white keys
        white_white_paint = skia.Paint(
            AntiAlias = True,
            Color = self.colors["marker_color_between_two_white"],
            Style = skia.Paint.kStroke_Style,
            StrokeWidth = 1,
        )

        current_center = 0

        # Check if prev and this key is white, keeps track of a current_center, create rect to draw and draw
        for index, key_index in enumerate(self.piano_keys.keys()):
            key = self.piano_keys[key_index]
            if not index == 0:
                prevkey = self.piano_keys[key_index - 1]
                if (prevkey.is_white) and (key.is_white):
                    current_center += self.tone_width
                    rect = skia.Rect(
                        current_center - self.semitone_width,
                        0,
                        current_center - self.semitone_width,
                        self.mmvskia_main.context.height
                    )
                    self.mmvskia_main.skia.canvas.drawRect(rect, white_white_paint)
                else:
                    current_center += self.semitone_width

        # Ask each key to draw their CENTERED marker
        for key_index in self.piano_keys.keys():
            self.piano_keys[key_index].draw_marker()

    # Draw a given note according to the seconds of midi content on the screen,
    # horizontal (note), vertical (start / end time in seconds) and color (channel)
    def draw_note(self, velocity, start, end, channel, note, name):

        # Get the note colors for this channel, we receive a dict with "sharp" and "plain" keys
        note_colors = self.colors[f"channel_{channel}"]
        
        # Is a sharp key
        if "#" in name:
            width = self.semitone_width * 0.9
            color1 = note_colors["sharp_1"]
            color2 = note_colors.get("sharp_2", color1)

        # Plain key
        else:
            width = self.tone_width * 0.6
            color1 = note_colors["plain_1"]
            color2 = note_colors.get("plain_2", color1)

        # Make the skia Paint
        note_paint = skia.Paint(
            AntiAlias = True,
            Style = skia.Paint.kFill_Style,
            Shader = skia.GradientShader.MakeLinear(
                points = [(0.0, 0.0), (self.mmvskia_main.context.width, self.mmvskia_main.context.height)],
                colors = [color1, color2]
            ),
            StrokeWidth = 2,
        )

        # Border of the note
        note_border_paint = skia.Paint(
            AntiAlias = True,
            Style = skia.Paint.kStroke_Style,
            ImageFilter = skia.ImageFilters.DropShadowOnly(3, 3, 30, 30, note_colors["border_shadow"]),
            # MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.0),
            # StrokeWidth = max(self.mmvskia_main.context.resolution_ratio_multiplier * 2, 1),
            StrokeWidth = 0,
        )
        
        # Horizontal we have it based on the tones and semitones we calculated previously
        # this is the CENTER of the note
        x = self.keys_centers[note]

        # The Y is a proportion of, if full seconds of midi content, it's the viewport height itself,
        # otherwise it's a proportion to the processing time according to a start value in seconds
        y = self.functions.proportion(
            self.config["seconds_of_midi_content"],
            self.viewport_height, #*2,
            self.mmvskia_main.context.current_time - start
        )

        # The height is just the proportion of, seconds of midi content is the maximum height
        # how much our key length (end - start) is according to that?
        height = self.functions.proportion(
            self.config["seconds_of_midi_content"],
            self.viewport_height,
            end - start
        ) 

        spacing = self.viewport_height / 512

        # Build the coordinates of the note
        # Note: We add and subtract half a width because X is the center
        # while we need to add from the viewport out heights on the Y
        coords = [
            x - (width / 2),
            y + (self.viewport_height) - height + spacing,
            x + (width / 2),
            y + (self.viewport_height) - spacing,
        ]

        # Rectangle border of the note
        # rect = skia.Rect(*coords)
        rect = skia.RRect(skia.Rect(*coords), 
            self.config["rounding"]["notes"]["x"],
            self.config["rounding"]["notes"]["y"]
        )
        
        # Draw the note and border
        self.mmvskia_main.skia.canvas.drawRRect(rect, note_paint)

        # Get paint, font
        if self.config["draw_note_name"]:
            paint = skia.Paint(AntiAlias = True, Color = skia.ColorBLACK, StrokeWidth = 43)

            height_size = self.font.getSpacing()
            text_size = self.font.measureText(name[:-1])

            self.mmvskia_main.skia.canvas.drawString(
                name[:-1],
                (x) - (text_size / 2),
                (y + (self.viewport_height) + spacing) - (height_size / 2),
                self.font, paint
            )

    def set_best_font(self):
        text_fits = 0

        while True:
            text_fits += 1

            font = skia.Font(skia.Typeface('Ubuntu'), text_fits)
            height_size = font.getSpacing()
            text_size = font.measureText("F#")

            if text_size > self.semitone_width:
                break
        
        self.font = skia.Font(skia.Typeface('Arial'), text_fits - 4)

    # Build, draw the notes
    def build(self, effects):

        # Clear the background
        screen_coords = [0.0, 0.0, self.mmvskia_main.context.width, self.mmvskia_main.context.height]
        bg1 = self.colors["background_1"]
        bg2 = self.colors.get("background_2", bg1)

        # Make the skia Paint and
        screen_paint = skia.Paint(
            AntiAlias = True,
            Style = skia.Paint.kFill_Style,
            Shader = skia.GradientShader.MakeLinear(
                points = [(0.0, 0.0), (screen_coords[2], screen_coords[3])],
                colors = [bg1, bg2]
            ),
        )
        self.mmvskia_main.skia.canvas.drawRect(skia.Rect(*screen_coords), screen_paint)

        # Draw the orientation markers 
        if self.config["do_draw_markers"]:
            self.draw_markers()

        # # Get "needed" variables

        time_first_note = self.vectorial.midi.time_first_note

        # If user passed seconds offset then don't use automatic one from midi file
        if "seconds_offset" in self.config.keys():
            offset = self.config["seconds_offset"]
        else:
            offset = 0
            # offset = time_first_note # .. if audio is trimmed?

        # Offsetted current time at the piano key top most part
        current_time = self.mmvskia_main.context.current_time - offset

        # What keys we'll bother rendering? Check against the first note time offset
        # That's because current_time should be the real midi key not the offsetted one
        accept_minimum_time = current_time - self.config["seconds_of_midi_content"]
        accept_maximum_time = current_time + self.config["seconds_of_midi_content"]

        # What notes are playing? So we draw a darker piano key
        self.notes_playing = {}

        # For each channel of notes
        for channel in self.vectorial.midi.timestamps.keys():

            # For each key message on the timestamps of channels (notes)
            for key in self.vectorial.midi.timestamps[channel]:

                # A "key" is a note if it's an integer
                if isinstance(key, int):

                    # This note play / stop times, for all notes [[start, end], [start, end] ...]
                    note = key
                    times = self.vectorial.midi.timestamps[channel][note]["time"]
                    delete = []

                    # For each note index and the respective interval
                    for index, interval in enumerate(times):

                        # Out of bounds completely, we don't care about this note anymore.
                        # We mark for deletion otherwise it'll mess up the indexing
                        if interval[1] < accept_minimum_time:
                            delete.append(index)
                            continue
                        
                        # Notes past this one are too far from being played and out of bounds
                        if interval[0] > accept_maximum_time:
                            break

                        # Is the current time inside the note? If yes, the note is playing
                        current_time_in_interval = (interval[0] < current_time < interval[1])
                        
                        # Append to playing notes
                        if current_time_in_interval:
                            self.notes_playing[note] = channel

                        # Either way, draw the key
                        self.draw_note(
                            # TODO: No support for velocity yet :(
                            velocity = 128,

                            # Vertical position (start / end)
                            start = interval[0],
                            end = interval[1],

                            # Channel for the color and note for the horizontal position
                            channel = channel,
                            note = note,

                            # Name so we can decide to draw a sharp or plain key
                            name = self.vectorial.midi.note_to_name(note),
                        )
                
                    # This is an interval we do not care about anymore
                    # as the end of the note is past the minimum time we accept a note being rendered
                    for index in reversed(delete):
                        del self.vectorial.midi.timestamps[channel][note]["time"][index]

        self.draw_piano()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class PianoKey:
    def __init__(self, mmv, vectorial, MMVSkiaPianoRollTopDown):
        self.mmvskia_main = mmv
        self.vectorial = vectorial
        self.piano_roll = MMVSkiaPianoRollTopDown
        self.config = self.piano_roll.config
        self.colors = self.piano_roll.colors

        # Key info
        self.key_index = None
        self.name = ""

        # Position, states
        self.center_x = None
        self.width = None
        self.height = None
        self.resolution_height = None
        self.active = False

    # Configure PianoKey by midi key index
    def by_key_index(self, key_index):
        self.note = key_index
        self.name = self.vectorial.midi.note_to_name(self.note)
        self.configure_color()
        print(f"{key_index}: {self.name}", end = "", flush = True)
    
    # Configure pressed, idle colors based on key name
    def configure_color(self):

        # Note is a sharp key, black idle, gray on press
        if "#" in self.name:
            self.color_3d_effect = self.colors["sharp_key_3d_effect"]
            self.color_active_1 = self.colors["sharp_key_pressed_1"]
            self.color_active_2 = self.colors["sharp_key_pressed_2"]
            self.color_idle_1 = self.colors["sharp_key_idle_1"]
            self.color_idle_2 = self.colors["sharp_key_idle_2"]
            self.is_white = False
            self.is_black = True
        
        # Note is plain key, white on idle, graw on press
        else:
            self.color_3d_effect = self.colors["plain_key_3d_effect"]
            self.color_active_1 = self.colors["plain_key_pressed_1"]
            self.color_active_2 = self.colors["plain_key_pressed_2"]
            self.color_idle_1 = self.colors["plain_key_idle_1"]
            self.color_idle_2 = self.colors["plain_key_idle_2"]
            self.is_white = True
            self.is_black = False
        
    # Draw this key
    def draw(self, notes_playing):

        away_ratio = 0.33

        # If the note is black we leave a not filled spot on the bottom, this is the ratio of it
        away = (self.height * (away_ratio)) if self.is_black else 0

        # Based on the away, center, width, height etc, get the coords of this piano key
        coords = [
            self.center_x - (self.width / 2),
            self.resolution_height - self.height,
            self.center_x + (self.width / 2),
            self.resolution_height - away,
        ]

        white_or_back = "white" if self.is_white else "black"

        # Rectangle border
        key_rect = skia.RRect(skia.Rect(*coords),
            self.config["rounding"]["piano_keys"][white_or_back]["x"],
            self.config["rounding"]["piano_keys"][white_or_back]["y"]
        )

        # Is the note active
        self.active = self.note in notes_playing.keys()

        if self.config["piano_key_follows_note_color"]:
            if self.active:
                channel = notes_playing[self.note]
                color1 = self.colors[f"channel_{channel}"]["plain_1"]
                color2 = self.colors[f"channel_{channel}"]["plain_2"]
            else:
                color1 = self.color_idle_1
                color2 = self.color_idle_2

        else:
            # Get the color based on if the note is active or not
            color1 = self.color_active_1 if self.active else self.color_idle_1
            color2 = self.color_active_2 if self.active else self.color_idle_2
        
        # Make the skia Paint and
        key_paint = skia.Paint(
            AntiAlias = True,
            # Color = color1,
            Style = skia.Paint.kFill_Style,
            Shader = skia.GradientShader.MakeLinear(
                points = [(0.0, self.mmvskia_main.context.height), (self.mmvskia_main.context.width, self.mmvskia_main.context.height)],
                colors = [color1, color2]),
            StrokeWidth = 0,
        )

        # The border of the key
        key_border = skia.Paint(
            AntiAlias = True,
            Color = skia.Color4f(0, 0, 0, 1),
            Style = skia.Paint.kStroke_Style,
            StrokeWidth = 1,
        )

        # Make flat top
        if self.is_black:
            bleed = self.config["rounding"]["piano_keys"][white_or_back]["x"] / 8
            flat_top_key_rect = skia.Rect(coords[0], coords[1] - bleed, coords[2], (coords[3] - (coords[3] - coords[1]) / 4) - bleed)
            self.mmvskia_main.skia.canvas.drawRect(flat_top_key_rect, key_paint)

        # Draw the key (we'll draw on top of it later)
        self.mmvskia_main.skia.canvas.drawRRect(key_rect, key_paint)

        # Draw the 3d effect
        if (not self.active):

            # One fourth of the away ratio
            three_d_effect_away = away + (self.height * (away_ratio / 4))

            # The coordinates considering black key's away
            three_d_effect_coords = [
                self.center_x - (self.width / 2),
                self.resolution_height - three_d_effect_away,
                self.center_x + (self.width / 2),
                self.resolution_height - away,
            ]

            # The paint
            three_d_effect_paint = skia.Paint(
                AntiAlias = True,
                Color = self.color_3d_effect,
                Style = skia.Paint.kFill_Style,
                StrokeWidth = 0,
            )

            rect = skia.RRect(skia.Rect(*three_d_effect_coords), 8, 8)

            # Draw the rectangle
            self.mmvskia_main.skia.canvas.drawRRect(rect, three_d_effect_paint)

        # Draw the border
        if not self.is_black:
            self.mmvskia_main.skia.canvas.drawRRect(key_rect, key_border)
    
    # Draw the markers ON THE KEY ITSELF, cutting through its center
    def draw_marker(self):

        # If the note is a G, it's a mid way reference on the piano
        # This considers G# keys only
        if "G" in self.name and self.is_black:
            color = self.colors["marker_color_g_sharp"]
        elif self.is_black:
            color = self.colors["marker_color_sharp_keys"]
        else:
            return
        
        if color is None:
            return

        # The marker paint
        marker = skia.Paint(
            AntiAlias = True,
            Color = color,
            Style = skia.Paint.kFill_Style,
            # StrokeWidth = 2,
        )

        # Draw through the entire vertical space of the screen
        rect = skia.Rect(
            max(self.center_x - (self.width / 10), 1),
            0,
            max(self.center_x + (self.width / 10), 1),
            self.resolution_height - self.height
        )
        self.mmvskia_main.skia.canvas.drawRect(rect, marker)