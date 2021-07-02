"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interpolation utility (smoothing values)

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

a = np.array

class SmoothVariable:
    # Value and ratio can be numpy array, just make sure to be the
    # same dimension y'know
    def __init__(self, value = None, ratio = 1):
        self.value, self.ratio = value, ratio
        self._target_is_current_value()

    # Initializer or short hand for setting target to current value, so we
    # basically ignore any future interpolation we want to do
    def _target_is_current_value(self):
        self.set_target(np.copy(self.value).astype(np.float64))

    # Set target value
    def set_target(self, target): self.target = target

    # Representation
    def __str__(self): return self.value

    # One is supposed to do like:
    #   foo = SmoothVariable(0, 0.75)
    #   foo += 10
    #   foo.next()
    #   foo.value -> 7.5
    def __add__(self, other): self.target += a(other).astype(np.float64); return self
    def __sub__(self, other): self.target -= a(other).astype(np.float64); return self

    # Interpolate
    def next(self, ratio = None):
        self.ratio = ratio or self.ratio
        self.value += (self.target - self.value) * self.ratio


