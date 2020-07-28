"""
===============================================================================

Purpose: Activation functions

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

from mmv.common.cmn_types import *
import math


class Functions:

    # Sigmoid function, put that last part in a graphic visualization software to understand
    # @smooth: how much steps are needed for X to get from -4 to 4 on the function (as they are some nice angle spots on the graph)
    # @x: the "biased" "this_position" step
    def sigmoid(self, x: Number, smooth: Number) -> Number:
        # Fit x from -4 to 4, 0 to 1
        fit = smooth*x - (smooth/2)
        return 1 / (1 + math.exp(-fit))

    # Calculate a linear proportion
    def proportion(self, a: Number, b: Number, c: Number) -> Number:
        # a - b
        # c - x
        # x = b*c/a
        return b*c/a


"""
How to "fit" the linear FFT into any shape we want?

I noticed that any polinomial in the form y = x^n with n >= 0, WILL hit the points
(0, 0) and (1, 1) but the curve shape depends on this n. That is because 0^n for every n diff 0 equals
zero and 1^n for any n {*note 1} will hit the point (1, 1).

What we can do is get a proportion of the index according to the total on a interval of [0, 1],
that is, if the maximum value is 20 and we're at position 10, this proportion will be 0.5, or half,
50%, if we're at number one, we'll be at 1/20, or 0.05, 5% of the way through it.

I want you to imagine the functions or go onto a online graph tool and put y=x^n and add a slider for n,
zoom in on the square points (0, 0) and (1, 1) and change the n. Think X as the input and Y as the output,
we're "modulating", applying a "fit function" to this proportion if we get a value between zero and one.

On the case we're at 0.5 the way through, if n=1, we do 0.5^1 which is itself, that is, linear, but
if you put n=2 and square 0.5, we'll be at the 0.25 mark.

Remember that X is our input and Y our output, you can see this clearly on the graph, when x=0.5, y=0.25 and
that it doesn't increase linearly, it starts slow then starts to speed up. (the same concept as derivatives,
d(x^2) is 2x so we're increasing our slope as X increases)

So after we apply this fitting thingy to the proportion number, we just have to multiply it back by
the maximum number on the sequence that we got the proportion from!! This way we "transposed", "fitted"
the indexes on a linear style into a shape we want in a new list.

We can do the same with any graph we want virtually, let's take the log10 for example, when x=1, log10(x)=0
and when x=10, log10(x) = 1, we can apply this same concept here. So we start at point 1 and find a proportion
from this index to the total between 0 and 9 since we're already at 1 and multiply back by the max number
and apply the function, so we'll get something like total*log10(1 + proportion(current_index is one, total is what))

*note 1: yes that is wrong, the lim_{n to infinity} (1 + 1/n)^n when you apply the limit rules
is (1 + 0)^infinity which is technically 1^infinity that evaluates to the Euler number e, (2.718281828..)
so if 1 is (as weird as this may seem) exactly one, then 1^infinity is 1, otherwise 1 is ever so
slightly more than 1 into that e number proportion it'll evaluate to e. This is why 1^infinity
is undefined, calculus 1 people :)
"""
class FitIndex:
    def __init__(self):
        self.functions = Functions()

    # Is out value between 
    def out_of_bounds(self, value: Number, above: Number, below: Number) -> bool:
        if value < below:
            return [True, below]
        if value > above:
            return [True, above]
        return [False]

    def polynomial(self, index: Number, total: Number, exponent: Number) -> Number:
        oob = self.out_of_bounds(index, total, 0)
        if oob[0]: return oob[1]

        index = (total) * (self.functions.proportion(total, 1, index) ** exponent)
        return index
    
    def log10(self, index: Number, total: Number) -> Number:
        oob = self.out_of_bounds(index, total, 0)
        if oob[0]: return oob[1]

        index = (total) * ( math.log(1 + self.functions.proportion(total - 1, 9, index), 10) )
        return index