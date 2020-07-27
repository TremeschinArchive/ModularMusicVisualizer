"""
===============================================================================

Purpose: Activation functions for Gaussian Blur modifier

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


# "ic" - Interpolation Changer, change the interpolation of the modifier

def ma_gaussian_blur_ic_low(interpolation: MMVInterpolation, average_audio_value: Number) -> None:
    interpolation.target_value =average_audio_value * 10

# default
def ma_gaussian_blur_ic_medium(interpolation: MMVInterpolation, average_audio_value: Number) -> None:
    interpolation.target_value = average_audio_value * 15

def ma_gaussian_blur_ic_high(interpolation: MMVInterpolation, average_audio_value: Number) -> None:
    interpolation.target_value = average_audio_value * 20


# "vc" - Value Changer functions, applied after interpolation

# default
def ma_gaussian_blur_vc_only_interpolation(interpolation: MMVInterpolation, average_audio_value: Number) -> Number:
    return interpolation.current_value