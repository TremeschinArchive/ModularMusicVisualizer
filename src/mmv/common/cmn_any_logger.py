"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: If no logger exists, create one logging handler outputting to 
system's stdout. Just importing this file will run its content and we should
be good to go

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
import sys

# If we're somehow loading / executing this file alone without MMV's
# main interface class, we'll have no logging handler going one so
# we empty out every logger handler and add one for outputting to
# system's stdout with not really any special formatting apart from
# the log level and the message string

# Get current logger if any
logger = logging.getLogger()

# If handlers list is not empty
if not logger.handlers:
    print("[cmn_any_logger.py] No logger found, creating one with StreamHandler(sys.stdout)")

    # Create basic logger
    logging.basicConfig(
        handlers = [logging.StreamHandler(sys.stdout)],
        level = logging.DEBUG,
        format = "[%(levelname)-7s] %(message)s",
    )
