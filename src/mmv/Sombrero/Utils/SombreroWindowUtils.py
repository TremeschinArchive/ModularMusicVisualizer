"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Refactor of some SombreroWindow functionality

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
import time
import uuid

import numpy as np


# Handler for messages that expire or doesn't
class OnScreenTextMessages:
    def __init__(self): self.contents = {}
    
    # Add some message to the messages list
    def add(self, message: str, expire: float, has_counter = True) -> None:
        logging.info(f"[OnScreenTextMessages] Add message: [{message}] [expire: {expire}]")
        self.contents[str(uuid.uuid4())] = {
            "message": message,
            "expire": time.time() + expire,
            "has_counter": has_counter}

        # Sort items chronologically
        self.contents = {k: v for k, v in sorted(self.contents.items(), key = lambda x: x[1]["expire"])}
    
    # Delete expired messages
    def next(self):
        expired_keys = []
        for key, item in self.contents.items():
            if time.time() > item["expire"]: expired_keys.append(key)
        for key in expired_keys: del self.contents[key]

    # Generator that yields messages to be shown
    def get_contents(self):
        self.next()

        # Process message, yield it
        for item in self.contents.values():
            message = ""
            if item["has_counter"]:
                message += f"[{item['expire'] - time.time():.1f}s] | "
            message += item["message"]
            yield message


class FrameTimesCounter:
    def __init__(self, fps = 60, plot_seconds = 2, history = 30):
        self.fps, self.plot_seconds, self.history = fps, plot_seconds, history
        self.last = time.time()
        self.counter = 0
        self.plot_fps = 60  # Otherwise too much info
        self.clear()
    
    # Create or reset the framtimes array
    def clear(self):
        self.frametimes = np.zeros((self.plot_fps * self.history), dtype = np.float32)
        self.last = time.time()
        self.first_time = True
    
    # Update counters
    def next(self):
        if not self.first_time:
            self.frametimes[self.counter % self.frametimes.shape[0]] = time.time() - self.last
        self.first_time = False
        self.last = time.time()
        self.counter += 1

    # Get dictionary with info
    def get_info(self):

        # Cut array in wrap mode, basically where we are minus the plot_seconds target
        plot_seconds_frametimes = self.frametimes.take(range(self.counter - (self.plot_seconds * self.plot_fps), self.counter), mode = "wrap")
        plot_seconds_frametimes_no_zeros = plot_seconds_frametimes[plot_seconds_frametimes != 0]

        # Simple average, doesn't tel much
        avg = np.mean(plot_seconds_frametimes_no_zeros)

        # Ignore zero entries, sort for getting 1% and .1%
        frametimes = self.frametimes[self.frametimes != 0]
        frametimes = list(reversed(list(sorted(frametimes))))
  
        return {
            "frametimes": plot_seconds_frametimes, "average": avg,
            "min": min(plot_seconds_frametimes_no_zeros, default = 1),
            "max": max(plot_seconds_frametimes_no_zeros, default = 1),
            "1%": np.mean(frametimes[0 : max(int(len(frametimes) * .01), 1)]),
            "0.1%": np.mean(frametimes[0 : max(int(len(frametimes) * .001), 1)]),
        }
