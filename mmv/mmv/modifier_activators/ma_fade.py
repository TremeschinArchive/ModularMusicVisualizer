"""
===============================================================================

Purpose: Activation functions for Fade modifier

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

# default
def ma_fade_ic_keep(interpolation: MMVInterpolation, average_audio_value: Number) -> None:
    return



# "vc" - Value Changer functions, applied after interpolation

# default
def ma_fade_vc_only_interpolation(interpolation: MMVInterpolation, average_audio_value: Number) -> Number:
    return interpolation.current_value