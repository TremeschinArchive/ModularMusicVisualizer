"""
===============================================================================

Purpose: Activation functions for Vignetting modifier

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


from mmv.mmv_interpolation import MMVInterpolation
from mmv.common.cmn_types import *

# width and height are final video resolution

# "ic" - Interpolation Changer, change the interpolation of the modifier

def ma_vignetting_ic_low(
        start_value: Number,
        interpolation: MMVInterpolation,
        average_audio_value: Number,
        width: Number,
        height: Number,
    ) -> None:

    interpolation.target_value = ( (start_value - 600 * average_audio_value) / 720) * height

# default
def ma_vignetting_ic_medium(
        start_value: Number,
        interpolation: MMVInterpolation,
        average_audio_value: Number,
        width: Number,
        height: Number,
    ) -> None:

    interpolation.target_value = ( (start_value - 800 * average_audio_value) / 720) * height

def ma_vignetting_ic_high(
        start_value: Number,
        interpolation: MMVInterpolation,
        average_audio_value: Number,
        width: Number,
        height: Number,
    ) -> None:

    interpolation.target_value = ( (start_value - 1200 * average_audio_value) / 720) * height


# "vc" - Value Changer functions, applied after interpolation

# default
def ma_vignetting_vc_only_interpolation(
        interpolation: MMVInterpolation,
        average_audio_value: Number,
        width: Number,
        height: Number,
    ) -> Number:
    return interpolation.current_value