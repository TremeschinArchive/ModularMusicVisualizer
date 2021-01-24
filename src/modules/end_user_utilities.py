"""
===============================================================================

Purpose: Check requirements.txt dependencies, downloads required ones if any

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


class ArgParser:
    def __init__(self, argv):
        self.argv = argv
        self.parse_argv()
        
    # Check for flags on argv
    def parse_argv(self):
        debug_prefix = "[ArgParser]"

        # Empty list of flags and kflags
        self.flags = []
        self.kflags = {}

        if self.argv is not None:

            # Iterate in all args
            for arg in self.argv[1:]:
                
                # Is a kwarg
                if "=" in arg:
                    arg = arg.split("=")
                    self.kflags[arg[0]] = arg[1]

                # Is a flag
                else:
                    self.flags.append(arg)
        
        self.auto_deps = "--auto-deps" in self.flags
        print(debug_prefix, "--auto-deps True") if self.auto_deps else print(debug_prefix, "--auto-deps False")

        if "render" in self.kflags.keys():
            render = self.kflags["render"]
            
            # Only two modes available
            assert render in ["gpu", "cpu"]

            print(debug_prefix, f"Render target is [{render}]")
            self.render = render
        else:
            print(debug_prefix, "No given render target flag, assuming [gpu]")
            self.render = "gpu"
        
        print(self.flags, self.kflags)