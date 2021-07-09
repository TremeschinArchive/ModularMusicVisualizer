"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: SVG flags icons -> PNG images

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
import logging
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import mmv
from mmv.Common.Download import Download
from mmv.Editor.Localization import Languages

PackageInterface = mmv.mmvPackageInterface()

# Need: inkscape on PATH
def MakeCountryFlags():
    dpfx = "[Magic.MakeCountryFlags]"

    for Key, Value in Languages.__dict__.items():
        if not "__" in Key:
            ThisLanguage = Languages.__dict__[Key]
            TempSourceSVGPath = PackageInterface.TempDir/"TempCountryFlag.svg"
            with open(TempSourceSVGPath, "w") as SourceSVG:
                URL = f"https://hatscripts.github.io/circle-flags/flags/{ThisLanguage.CountryFlag}.svg"
                SVG = Download.GetHTMLContent(URL)
                logging.info(f"{dpfx} SVG content is: {SVG}")
                SourceSVG.write(SVG)
            FinalPNG = PackageInterface.DataDir/"Image"/"Icon"/"Flags"/f"{ThisLanguage.CountryFlag}.png"
            FinalPNG.parent.mkdir(exist_ok=True)
            logging.info(f"{dpfx} Final PNG is {FinalPNG}")
            Command = ["inkscape", str(TempSourceSVGPath), "-o", str(FinalPNG)]
            logging.info(f"{dpfx} Run command: {Command}")
            subprocess.run(Command)
            os.remove(str(TempSourceSVGPath))

def Main():
    if "MakeCountryFlags" in sys.argv: MakeCountryFlags()

if __name__ == "__main__":
    Main()


