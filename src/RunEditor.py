"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Node Editor testing

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
import os
# Add current directory to PATH so we find the "mmv" package
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import mmv
import time


def Main():
    PackageInterface = mmv.mmvPackageInterface()
    Editor = PackageInterface.GetEditor()
    Editor.InitMainWindow()

    while True: 
        try: time.sleep(0.5)
        except KeyboardInterrupt:
            Editor.Exit(); break

        if Editor._Stop: break

    sys.exit(0)


if __name__ == "__main__":
    Main()
