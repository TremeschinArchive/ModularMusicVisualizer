"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: Mostly solving a time-frequency domain on when to update / call
functions based on a fixed frequency

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
import time


# The one we add to BudgetVsyncManager
class BudgetVsyncClient:
    def __init__(self, Frequency, Callable, SomeContextToEnter=None):
        self.Frequency, self.Callable = Frequency, Callable
        self.SomeContextToEnter = SomeContextToEnter
        self.NextCall = time.time()
        self._Iteration = 0

    # Do our action, set NextCall timer
    def __call__(self):
        if self.SomeContextToEnter is not None:
            with self.SomeContextToEnter:
                self.Callable()
        else:   self.Callable()
        self._Iteration += 1
        self.NextCall = time.time() + self.Period
        return self

    @property
    def Period(self): return (1/self.Frequency)

    def __str__(self): return (
        f"[BudgetVsyncClient] "
        f"[Frequency: {self.Frequency:.2f}Hz] "
        f"[Callable: {self.Callable}]"
    )

class BudgetVsyncManager:
    def __init__(self):
        self.Targets = []

    # Add some Vsync callable
    def AddVsyncTarget(self, T: BudgetVsyncClient):
        self.Targets.append(T)

    # Do we have this target to be called already?
    def HaveTarget(self, T: BudgetVsyncClient):
        return T in self.Targets

    # Add target if does not exist
    def AddVsyncTargetIfDNE(self, T: BudgetVsyncClient):
        if self.HaveTarget(T): return
        self.AddVsyncTarget(T)

    # Run this on the main thread
    def Start(self):
        while True:
            self.DoNextAction()

    def DoNextAction(self):
        # Do nothing if don't have Targets
        if len(self.Targets) == 0: time.sleep(0.1); return

        # Get the nearest Next Call
        Closest = sorted(self.Targets, key=lambda Item: Item.NextCall)[0]

        # Sleep until it, call the VsyncedCallable (also calculates NextCall)
        time.sleep(max(Closest.NextCall-time.time(), 0))
        return Closest()
            