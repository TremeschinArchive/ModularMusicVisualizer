"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Base module abstraction

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

class BaseModule:
    def init(self, sombrero_window):
        self.sombrero_window = sombrero_window
        self.context = self.sombrero_window.context
        self.messages = self.sombrero_window.messages
        self.sombrero_mgl = self.sombrero_window.sombrero_mgl
        self.ACTION_MESSAGE_TIMEOUT = self.sombrero_window.ACTION_MESSAGE_TIMEOUT
        