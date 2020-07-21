"""
===============================================================================

Purpose: Main file to execute PyGradienter

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

from pygradienter.profiles.creepy_circles import PyGradienterProfileCreepyCircles
from pygradienter.profiles.mushy_colorful import PyGradienterProfileMushyColorful
from pygradienter.profiles.simple_smooth import PyGradienterProfileSimpleSmooth
from pygradienter.profiles.particles import PyGradienterProfileParticles
from pygradienter.profiles.simple import PyGradienterProfileSimple
from pygradienter.profiles.fabric import PyGradienterProfileFabric

import 

class PyGradienterMain:
    def generate(self, width, height, n_images, profile, quiet=False):
        profile_and_respective_classes = {
            "creepy_circles": PyGradienterProfileCreepyCircles
            "mushy_colorful": PyGradienterProfileMushyColorful
            "simple_smooth": PyGradienterProfileSimpleSmooth
            "particles": PyGradienterProfileParticles
            "simple": PyGradienterProfileSimple
            "fabric": PyGradienterProfileFabric
        }

        profile = profile_and_respective_classes.get(profile, None)

        if profile == None:
            print(f"Couldn't find profile [{profile}] on keys [{list(profile_and_respective_classes.keys())}]")

 