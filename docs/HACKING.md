# Understanding the code

In this file I'll talk about how the code of the Modular Music Visualizer is organized so you can have some idea on where to start _hacking_ (modifying) it or looking on how it works, learning from it.

Honestly, MMV's code isn't trivial. I'm more of a applied maths dude, I like a lot getting the intuition of stuff before doing / coding it so it is structured the way I broke down this problem of "Code a music visualizer" internally myself.

As a way to reduce the entry level of contributors / people wanting to know how it works I'll write in medium details here the intuitions of MMV, tell where I used some features of the language as well as a quick overview on topics you should know to understand the code with easier time.

## Classes

I heavily use classes on MMV, in shorthand they are a way of creating and organizing variables and methods (functions) into a "group" what we call an **object**.

I somewhat abuse Python's modularity regarding its Object Oriented Programming components, so don't expect "classic" OOP structure here but something similar to.

I won't teach classes as this is out of the scope of how I structured MMV.

### Duck Typing

I think the best example to demonstrate why classes are useful in the MMV project is what we call **duck typing**.

Given two classes A and B, if they have a common method name and / or attributes names we can do the following:

```python
class A:
    def next(self):
        # ...

class B:
    def next(self):
        # ...

obj_a = A()
obj_b = B()

objects = [obj_a, obj_b]

for item in objects:
    item.next()
```

_"If it looks like a duck and quacks like a duck, it's a duck"_

What we can infer from this analogy is that on both cases, class A and B we having a common method called `.next()`, we can call that method on the objects instances regardless their type.

If you come from a compiled language this is similar to polymorphism.

This is used a LOT on the interpolation classes like MMVInterpolation and all the MMVModifiers and virtually on every MMVSkiaImage and MMVSkiaVectorial.

See file `mmv_animation.py`, `.next()` function, we loop through every item on the layers calling their `.next()` and `.blit()` functions.

### References to objects

One important fact in this snippet is that **both obj_a and obj_b point to a location in the memory.**

If you run `print(obj_a)` you'll see something like:

- `<__main__.A object at 0x7f33022751c0>`

This part `0x7f33022751c0` is a location on the memory of your computer the object is stored on. (will probably / almost certainly be different in yours computer)

If you modify the code to do something like:

```python
class A:
    def my_memory_location(self):
        print(self)

a = A()

print(a)
a.my_memory_location()
```

This will print:

- `<__main__.A object at 0x7f330235a160>`
- `<__main__.A object at 0x7f330235a160>`

Notice that the `self` keywork inside a class is a reference to the object.. it**self**.

But wait, duck typing can use and abuse of this!! How?

#### The Main Class

The primary reason I stressed on this `self` keyword is that, the way MMV is organized, it boils down to this:

```python
# Holds runtime / configuration variables.
class Context:
    def __init__(self):
        self.fps = 60
        self.width = 1280
        self.height = 720

        self.audio_duration = None # We don't know yet!!


class Audio:
    def get_audio_duration(self, path):
        # Do trickery to find the audio duration

        # For demonstration purposes
        # let's consider a 8 second audio
        duration = 8 

        # # # # # # # # # # # # # # # # # # # #

        return duration


class Main:
    def __init__(self):
        # Create our Context class INSIDE the Main class
        self.context = Context()

        # Create our Audio class INSIDE the Main class
        self.audio = Audio()

        # Demonstration purposes configure method
        self.configure()
    
    def configure(self):
        # Here we assign to the Context class we created, the duration of a demo file
        self.context.audio_duration = self.audio.get_audio_duration("file.ogg")

# Run Main class
main = Main()
```

You should get somewhat used to this to move forward, try toying a bit with it.

Now we'll abuse this. I'll create a `Core` class where it'll handle the core loops and calls everybody. Read the code first so I can explain later on (most of it is the same as this previous one).



```python
# Holds runtime / configuration variables.
class Context:
    def __init__(self):
        self.fps = 60
        self.width = 1280
        self.height = 720

        self.audio_duration = None # We don't know yet!!


class Audio:
    def get_audio_duration(self, path):
        # Do trickery to find the audio duration

        # For demonstration purposes
        # let's consider a 8 second audio
        duration = 8 

        # # # # # # # # # # # # # # # # # # # #

        return duration

class Core:
    # IMPORTANT: We get a "main" variable that is a reference to the Main class
    def __init__(self, main):
        self.main = main

    # We moved the Configure class here because our Main class is basically a 
    # wrapper and communicator for everybody.
    def configure(self):
        # Here we assign to the Context class we created, the duration of a demo file
        # IMPORTANT: see that we use self.main.* to access Main class atributes!!
        self.main.context.audio_duration = self.main.audio.get_audio_duration("file.ogg")

    # Demonstration run class
    def run(self):
        self.configure()
        # ... continues

class Main:
    def __init__(self):
        # Create our Context class INSIDE the Main class
        self.context = Context()

        # Create our Audio class INSIDE the Main class
        self.audio = Audio()

        # We pass a reference to THIS class, the MAIN one to the class Core!!
        self.core = Core(self)

        # Instead of configuring we now do:
        self.core.run()
  
# Run Main class
main = Main()
```

The very own thingy I wanted to show up until now is exactly this part inside the Core class, where we can access `self.mmv.*` stuff from it.

In fact inside that `run()` method on Core class, we can replace that by:

```python
def run(self):
    self.main.core.configure()
```
_(this is redundant code)_

In fact we can keep going!!

```python
def run(self):
    self.main.core.main.core.main.core.configure()
```
_(even more redundant code)_

**I pass a reference of the Main class to basically everyone so I can access anyone, anywhere.**

In fact if we had let's say a class that deals with Video inside the Core class, we can do something like:

```python
class Video:
    def __init__(self, main):
        self.main = main
    
    def start(self):
        # Demonstration purposes method
        self.create_video_pipe(
            width = self.main.context.width,
            height = self.main.context.height,
            fps = self.main.context.fps,
        )

    # See closely this "bunch of arguments", it's the next topic
    def create_video_pipe(self, bunch_of_arguments):
        # ... do stuff
```

We get the main class on `Video.__init__`, so when creating the video pipe we can directly access the runtime vars on Main's class Context class instance, `self.context` var there (Main), `self.main.context` var here (Video).

That's about it!! When you see any `self.mmv_main` on the code, it is referring to the `MMVSkiaMain` class where it creates everybody so we can communicate anyone!!


## "bunch of arguments"

In the previous section we can see that the `create_video_pipe` method should have A LOT of stuff, I can think of:

- Width
- Height
- FPS
- Quality
- Codec
- Audio file input
- Filters?
- Resolution

One thing I started doing to "solve" this issue is using Python's `kwargs`.

On Python the `*` operator have another "hidden" function, it is called the **unpack** operator.

If you come from compiled languages such as C++, don't confuse with pointers, or Rusts's ownership and borrowing model.

```python
# This function multiplies the index of the argument times its value
def complicated_function_multiple_inputs(a, b, c):
    return (a*1) + (b*2) + (c*3)

# We can
complicated_function_multiple_inputs(1, 3, 2)

# Or..
values = [1, 3, 2]
complicated_function_multiple_inputs(*values)
```

This is one use of the unpack operator, I did use it a couple times on MMV, however I'm more interested in this utility here:

```python
# This function multiplies the index of the argument times its value
def another_complicated_function(*values):
    return sum([index * value for index, value in enumerate(values)])

values = [3, 2, 6, 7, 9, 20]
result = another_complicated_function(*values)
```

See here I used two unpack operators so I can input as much items I want on the function and it'll always work. But now, if we write this:

- `another_complicated_function(*values, other=4)`

Even though `other` is a number, it's not caught by the function. Why? Because it is a **keyed argument**.

The exponent operator `**` also happens to be a unpack operator, but for these shiny keyed arguments.

Before saying how MMV works with this, ... :

```python
dictionary = {
    "file_name": "test.ogg",
    "duration": 3,
    "format": "ogg",
}

# Traditional method
fname = dictionary["file_name"]

# If we're not sure if key is on dict
if "duration" in dictionary.keys():
    duration = dictionary["duration"]
```

This is where the `.get()` operator comes to save us. It's syntax is pretty simple:

- `object.get(key, default)`

Take a look at this:

```python
# User entered options
options = {
    "output_name": "video.mkv",
    "input_audio": "something.ogg",
}

# We must have a input_audio, None means error!
input_audio = options.get("input_audio", None)

if input_audio is None:
    exit("Input audio not found")

# Try getting the "fps" key on the options dictionary, defaults to 60 if not found.
fps = options.get("fps", 60)
```

As a general rule of thumb MMV code I'm following this style now: (inconsistent cause I switched mid way coding it)


```python
"""
kwargs:
{
    "key": value type
        Explain what it does
    "batch_size": int
        N of the FFT
    "that": bool
        Enables that feature
}
"""
def anything(**kwargs):
    fps = kwargs.get("fps", 60)
    batch_size = kwargs.get("batch_size", 2048)

anything(
    fps = 30,
    other = "waluigi",
    that = False,
)
```
_(this function would be inside a class but for the sake of simplicity it isn't)_

See I abuse kwargs by just throwing in arguments for the function to catch. 

It's optimal to leave a docstring before it so we know what arguments to pass and what to expect.


## Polar Coordinates

Usually this topic is taught on Calculus 2 classes, but the start of it doesn't require any calculus tools, in fact, only up to high school trigonometry.

Think how you can define a point in the rectangular grid on the XY plane.

Yes, coordinates, _(x, y)_ to be more precise.

The difference between rectangular and polar coordinates is that, instead of an _(x, y)_ point, we have a _(r, θ)_ one. θ is the greek letter "Theta".

- `r`: An distance from the polar (center of graph)
- `θ`: An counter clockwise angle relative to the "polar axis", the X axis on rectangular.

Basically we define a point with an angle and a distance from the origin.

You probably can see where this is useful, spoiler alert: radial music bars.

From this we have a few relationships and conversions from rectangular to polar equations:

- `x² + y² = r²`
- `x = r.cos(θ)`
- `y = r.sin(θ)`

This means that you can make the following transformation between the two.:

- `(x, y) = (r.cos(θ), r.sin(θ))`

Where does this comes from? See the right triangle formed when you walk away X units and climb up Y units, you'll climb a certain angle as well.

Applying the pythagoras theorem, we have our first relation.

When we see at the Y axis we climbed and the angle, we have:

- `sin(θ) = y/r`

Just a matter of multiplying the whole equation by `r` to get to that relation, same with `cos(θ)`.

If we divide `y/x` we get:

`y/x = (r.sin(θ) / r.cos(θ)) --> y/x = tan(θ)`

We can also from all these coordinates isolate our `θ`:

- `x = r.cos(θ) --> θ = acos(x/r)`
- `y = r.sin(θ) --> θ = asin(y/r)`

`acos` and `asin` are the inverse of their respective trigonometry function.

`sin(30°) = 0.5  -->  asin(0.5) = {30°, 150°}`

We get an extra number `150°` but that is because the symmetry with the Y axis.

Why this is useful? Very simple, for making the radial music bars instead of I don't even know how the math would be, finding points inside a circumference given by the equation:

- `(x-a)² + (y-b)² = r²`

Finding the appropriate angles and proportions would be pain, so the polar coordinates saves us (literally).

We define the music bars with a minimum distance from the center (usually the radius of the logo image) and the angle is just a proportion of that index to the total numbers of bars, in proportion to half a turn (180° or π radians.)

Then we just convert back to rectangular coordinates and voilà, we have the peak of that bar, just draw from the center of the visualizer up to that _(x, y)_ pixel on the screen and we're set!!