"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: 

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
import numpy as np
import logging


class MMVShaderValuesInterpolator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.instructions = {
            "mmv_audio_rms": [],
            "mmv_audio_std": [],
            "mmv_audio_fft_radial": [],
            "mmv_audio_fft_linear": [],
        }
        self.pipeline = {}

    def parse_used_variables(self, names: list):
        debug_prefix = "[MMVShaderValuesInterpolator.parse_used_variables]"
        logging.info(f"{debug_prefix} Matching for used variables and adding interpolators")

        # Iterate
        for full_name in names:
            logging.info(f"{debug_prefix} [{full_name}]")

            # They share the same prefix for the ratios
            for match_name in [f"mmv_audio_{x}" for x in ["rms", "std", "fft_radial", "fft_linear"]]:
                
                # Substring matches
                if match_name in full_name:

                    # "mmv_audio_rms_0_23" -> "0_23"
                    t = full_name.replace(match_name + "_", "").split("_")

                    # "0_23" -> 0.23f
                    ratio = float(f"{t[0]}.{t[1]}")

                    logging.info(f"{debug_prefix} :: Matched [{full_name}] ratio [{ratio}]")
                    self.instructions[match_name].append(ratio)

        # Convert to numpy arrays
        self.instructions = {k: np.array(v, dtype = np.float32) for k, v in self.instructions.items()}
        logging.info(f"{debug_prefix} Instruction on ratios: {self.instructions}")

    def next(self, data):
        keys = list(data.keys())

        for match_name in [f"mmv_audio_{x}" for x in ["rms", "std", "fft_radial", "fft_linear"]]:
            if (match_name in keys):

                # Ratios to interpolate (if any)
                ratios = self.instructions[match_name]

                # If we have some ratios
                if ratios.shape[0] > 0:

                    # The data to feed
                    feed = data[match_name]

                    for ratio in ratios:
                        str_ratio = str(ratio).replace(".", "_")
                        var_name = f"{match_name}_{str_ratio}"

                        # Firs time, just add original data
                        if not var_name in self.pipeline:
                            self.pipeline[var_name] = feed
                        else:
                            # Interpolate on ratios
                            self.pipeline[var_name] = self.pipeline[var_name] + (feed - self.pipeline[var_name]) * ratio

        return self.pipeline
