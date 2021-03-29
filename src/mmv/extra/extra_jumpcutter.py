"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Following carykh's JumpCutter idea

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

from mmv.common.cmn_audio import AudioProcessing
from tqdm import tqdm
import numpy as np
import threading
import logging
import math


class JumpCutter:
    def __init__(self, ffmpeg_wrapper):
        debug_prefix = "[JumpCutter.__init__]"
        self.audio_processing = AudioProcessing()
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.not_flipped = 0
        self.finished = False

    def configure(self, batch_size = 8096, sample_rate = 48000, target_fps = 60):
        self.batch_size = batch_size
        self.sample_rate = sample_rate
        self.target_fps = target_fps

    # Read a .wav file from disk and gets the values on a list
    def init(self, audio_path: str) -> None:
        debug_prefix = "[JumpCutter.init]"
        self.audio_path = audio_path

        logging.info(f"{debug_prefix} Reading total steps of audio in path [{audio_path}], should take 20 seconds per 1h of footage")

        # Calculate total steps
        self.total_steps = 0
        for _ in self.read_progressive():
            self.total_steps += 1
        logging.info(f"{debug_prefix} Total steps: [{self.total_steps}]")

        # Calculate duration
        self.duration = (self.total_steps * self.batch_size) / self.sample_rate
        logging.info(f"{debug_prefix} Un-jumped duration: [{self.duration}]")

    # Pro
    def read_progressive(self):
        for batch in self.ffmpeg_wrapper.raw_audio_from_file(
                input_file = self.audio_path, batch_size = self.batch_size,
                sample_rate = self.sample_rate, channels = 2):
            yield batch

    # Start jumpcutter processing
    def start(self, silent_speed, sounded_speed, silent_threshold):
        debug_prefix = "[JumpCutter.start]"

        # Assign config
        self.silent_speed = silent_speed
        self.sounded_speed = sounded_speed
        self.silent_threshold = silent_threshold

        # Info dict
        self.info = {
            "playback_audios" : {},
            "deformation_points": {},
        }
        
        logging.info(f"{debug_prefix} Calculating silent regions on Audio File, should take a while (but faster than rendering final video)..")

        # Progress bar
        progress_bar = tqdm(
            total = self.total_steps,
            unit = " slices",
            position = 1,
            dynamic_ncols = True,
            colour = '#00ff00',
            smoothing = 0.07,
        )
        progress_bar.set_description("Processing JumpCutter Audio     ")

        # Absolute time and how much samples we sliced so far
        self.current_absolute_time_no_deforming = 0
        cumulative_audio_to_process = []
        self.current_deformed_time = 0
        total_sliced = 0
        last = None
        step = 0
        
        # Iterate
        for batch in self.read_progressive():
            cumulative_audio_to_process.append(batch)

            # Mono audio
            mono = (batch[0] + batch[1]) / 2

            # Cut the mono slice and find min and max values
            min_max = [np.min(np.abs(mono)), np.max(np.abs(mono))]

            # Get target speed
            is_sounded = min_max[1] > self.silent_threshold

            if is_sounded:
                new = "sounded"
                self.this_speed = self.sounded_speed
            else:
                new = "silent"
                self.this_speed = self.silent_speed

            # First pass, consider flipped is False and last is the new one
            if last is None:
                last = new
                flipped = False
            
            # Second+ pass, flipped is if both aren't equal (last \neq new)
            else:
                flipped = last != new

            # If we flipped
            if flipped:

                # Either way we start with the raw cut as the pitch shifted one
                self.raw_pcm_processing = np.concatenate(cumulative_audio_to_process, axis = 1)
                cumulative_audio_to_process = []
            
                # Only need to process if speed is different than 1
                if (self.this_speed != 1):

                    # Size after resampling, so we do or not do it (return zeros or resampled)
                    size = self.raw_pcm_processing.shape[1] / self.this_speed

                    # Too short audio, send zeros
                    if size < 128:
                        self.raw_pcm_processing = np.zeros((2, int(size)))

                    else:
                        # Pitch shift accordingly
                        self.raw_pcm_processing = self.pitch_shift_slice(self.raw_pcm_processing, - 12 * math.log2(self.this_speed))

                        # Resample ("truncate" the audio)
                        self.raw_pcm_processing = np.array([
                            self.audio_processing.resample(self.raw_pcm_processing[0], self.sample_rate * self.this_speed, self.sample_rate),
                            self.audio_processing.resample(self.raw_pcm_processing[1], self.sample_rate * self.this_speed, self.sample_rate),
                        ])
                    
                # "Riemann summation" with limit \neq 0
                this_slice_N_samples = self.raw_pcm_processing.shape[1]

                # Mark there is at least some data and up to what index we can work with
                total_sliced += this_slice_N_samples

                # Calculate timings
                self.current_deformed_time = (total_sliced / self.sample_rate)
                self.current_absolute_time_no_deforming = (self.batch_size * step) / self.sample_rate
                self.this_slice_duration = (this_slice_N_samples * self.this_speed) / self.sample_rate

                # Yield data
                yield self.yield_deformation()
                yield self.yield_raw_pcm()
            else:
                self.not_flipped += 1

            progress_bar.update(1)
            step += 1
            
        # End, yield last data
        yield self.yield_deformation()
        yield self.yield_raw_pcm()
        progress_bar.close()
        self.finished = True

    # Pitch shift some audio slice by a certain amount of Hertz
    def pitch_shift_slice(self, audio_slice, ratio):
        import librosa
        return np.array([
            librosa.effects.pitch_shift(audio_slice[0], self.sample_rate, n_steps = ratio),
            librosa.effects.pitch_shift(audio_slice[1], self.sample_rate, n_steps = ratio)
        ])
    
    # # Yield data

    def yield_deformation(self):
        return {
            "type": "deformation",
            "speed": self.this_speed,
            "deformation_point": [
                self.current_deformed_time,
                self.current_absolute_time_no_deforming,
            ],
        }
    
    def yield_raw_pcm(self):
        return {
            "type": "raw_pcm",
            "data": self.raw_pcm_processing,
        }


