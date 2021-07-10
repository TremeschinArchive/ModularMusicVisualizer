"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Toolkit for writing shader. HEAVY metaprogramming

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
import copy
from pathlib import Path


# Yeet values from __init__ as self. values (overkill shorthand..)
def assign_locals(data):
    for key, value in data.items():
        if key != "self": data["self"].__dict__[key] = value


# # Abstractions

# Create contents dictionary
class HasContents:
    def __init__(self): self.contents = []
    def _add(self, content): self.contents.append(content) 

# When you instantiate Class()(parent_obj) you call .add to the parent
class CallableAddToParent:
    def __call__(self, parent): self.parent = parent; parent._add(self)

# One can search the contents of this object for stuff
# like matching classes or names
class Searchable(HasContents):
    def __init__(self): super().__init__()

    @property # Every Searchable / HasContents instances
    def everyone(self): yield from self.__get_everyone()

    # Recursively search because this item is Searchable; f we have contents then search that (core idea)
    def __get_everyone(self):
        for stuff in self.contents:
            if issubclass(type(stuff), Searchable): yield from stuff.everyone
            if issubclass(type(self), HasContents): yield stuff

    # Search functions, they return list of candidates, preferably will only have one..

    # Search for some specific class instance like search_class(IO) will yield all the IOs
    def search_class(self, who): return [stuff for stuff in self.everyone if isinstance(stuff, who)]

    # If item has attribute name (functions, placeholders) then match against it
    def search_by_name(self, name): return [stuff for stuff in self.everyone if ((hasattr(stuff, "name")) and (stuff.name == name))]

    # Search some placeholder
    def search_placeholder(self, name): return [ph for ph in self.search_by_name(name) if isinstance(ph, PlaceHolder)]



# Build method will only yield each content being built to a plain list, we can override this though
class SimpleBuildableChilds:
    def build(self, indent = "") -> list:
        return [built for item in self.contents for built in item.build(indent = indent)]

# Return self if entered, do nothing when exit
class SimpleEnterable:
    def __exit__(self, *args, **kwargs): pass 
    def __enter__(self): return self

# You can put this class on a with statement, it holds the content
#
# with SomeClass() as foo:
#     Include("path")(foo)
#
class WithScopedAddToParent(Searchable, SimpleBuildableChilds):
    def __init__(self): super().__init__()
    def __enter__(self): return self
    def __call__(self, parent): self.parent = parent; return self
    def __exit__(self, *args, **kwargs): self.parent._add(self)




# # Functionality, complete line statements



class Version(CallableAddToParent):
    def __init__(self, number): self.number = number
    def build(self, indent = "") -> list: return [f"#version {self.number}"]

class Define(CallableAddToParent):
    def __init__(self, what): self.what = what
    def build(self, indent = "") -> list: return [f"#define {self.what}"]

class Include(CallableAddToParent):
    def __init__(self, file): self.file = file
    def build(self, indent = "") -> list:
        data = Path(self.file).resolve().read_text()
        ret = [f"// // Include [{self.file}]\n"]
        for line in data.split("\n"):
            ret += [f"{indent}{line}"]
        ret += [f"\n// // End Include [{self.file}]"]
        return ret

# # Variables, Uniforms
class Uniform(CallableAddToParent):
    def __init__(self, var_type, name, value = None): assign_locals(locals())
    def build(self, indent = "") -> list: return [f"{indent}uniform {self.var_type} {self.name};"]
class Variable(CallableAddToParent):
    def __init__(self, var_type, name, value): assign_locals(locals())
    def build(self, indent = "") -> list: return [f"{indent}{self.var_type} {self.name} = {self.value};"]

# # Return stuff
class Return(CallableAddToParent):
    def __init__(self, what): self.what = what
    def build(self, indent = "") -> list: return [f"{indent}return {self.what};"]
class FragColor(CallableAddToParent):
    def __init__(self, what): self.what = what
    def build(self, indent = "") -> list: return [f"{indent}fragColor = {self.what};"]

# One input or output marked variable, communication between vertex, geometry and fragment shader
class IO(CallableAddToParent):
    def __repr__(self): return f"<IO {str(id(self))[-4:]} name:\"{self.name}\" mode:\"{self.mode}\">"
    def __init__(self, glsltype, name, use = True, prefix = True, mode = "io", flat = False):
        assign_locals(locals())
        {"io": self.do_input_and_output, 'i': self.do_only_input, 'o': self.do_only_output}.get(mode, "io")()

    def build(self, indent = "") -> list:
        R = []
        prefix = "flat " if self.flat else ""
        if "i" in self.mode: R += [f"{indent}{prefix}in {self.glsltype} {self.in_name};"]
        if "o" in self.mode: R += [f"{indent}{prefix}out {self.glsltype} {self.out_name};"]
        return R

    def do_only_input(self): self.mode = "i"
    def do_only_output(self): self.mode = "o"
    def do_input_and_output(self): self.mode = "io"

    @property
    def in_name(self) -> str:
        if self.prefix: return f"in_{self.name}"
        return f"{self.name}"
    @property
    def out_name(self) -> str:
        if self.prefix: return f"out_{self.name}"
        return f"{self.name}"

# Alpha composite function from sombrero specification
class AlphaComposite(CallableAddToParent):
    def __init__(self, old, new, target): assign_locals(locals())
    def build(self, indent = "") -> list: return [f"{indent}{self.target} = mAlphaComposite({self.old}, {self.new});"]

class GammaCorrection(CallableAddToParent):
    def __init__(self, assign, who, gamma): assign_locals(locals())
    def build(self, indent = ""): return [f"{indent}{self.assign} = pow({self.who}, vec4(1.0 / {self.gamma}));"]
 
# Define something on your own!
class CustomLine(CallableAddToParent):
    def __init__(self, content): self.content = content
    def build(self, indent = "") -> list: return [f"{indent}{self.content};"]

# Incomplete statement, meant to be used alongside some other one. They also return strings
# when called inside fstrings, makes sense since we want to just f"something {partialstatement}"
# and no need to directly call build on them
class PartialStatement:
    def __repr__(self): return self.build()

class Texture(PartialStatement):
    def __init__(self, sampler2D, uv): assign_locals(locals())
    def build(self, indent = "") -> str: return f"texture({self.sampler2D}, {self.uv})"


# # Scoped


class Function(WithScopedAddToParent):
    def __init__(self, return_type, name, arguments):
        super().__init__(); assign_locals(locals())

    def build(self, indent = "") -> list:
        data = [f"{indent}{self.return_type} {self.name}({self.arguments}) {{"]
        for item in self.contents:
            data += [f"{indent}{line}" for line in item.build("    " + indent)]
        data += [f"{indent}}}"]
        return data


class PlaceHolder(Searchable, CallableAddToParent, SimpleBuildableChilds):
    def __repr__(self): return f"<PlaceHolder {str(id(self))[-4:]} \"{self.name}\" {self.contents}>"
    def __init__(self, name): super().__init__(); assign_locals(locals())


# # Mappings


class GenericMapping:
    def __init__(self, **config): assign_locals(locals())

    # We need where to place (parent =~= PlaceHolder), the main sombrero mgl and the shader
    def __call__(self, sombrero_shader, parent, sombrero_mgl):
        assign_locals(locals()); self.parent._add(self)

    # Return uniform type name;
    def build(self, indent = ""):
        self.action()
        for item in self.info:
            if isinstance(item, Uniform):
                item( self.sombrero_shader.Uniforms )
        return []

class TextureImage(GenericMapping):
    def action(self): self.info = self.sombrero_mgl.map_image(**self.config)
class TextureShader(GenericMapping):
    def action(self): self.info = self.sombrero_mgl.map_shader(**self.config)
class TexturePipeline(GenericMapping):
    def action(self): self.info = self.sombrero_mgl.map_pipeline_texture(**self.config)


# # Main classes


# A Shader is basically a placeholder that have some inputs and outputs variables.
class SombreroShader(Searchable, SimpleBuildableChilds, SimpleEnterable):
    def __init__(self): super().__init__()
    def __repr__(self): return f"<Shader {self.contents}>"
    def copy(self): return copy.deepcopy(self)
    def build(self, indent = "") -> str:
        return '\n'.join( [built for item in self.contents for built in item.build(indent = indent)] )

    # Get In / Outs elements from the contents
    def get_in_outs(self) -> list: return self.search_class(IO)

    @property
    def Mappings(self): return self.search_placeholder("Mappings")[0]
    @property
    def UserShader(self): return self.search_placeholder("UserShader")[0]
    @property
    def Uniforms(self): return self.search_placeholder("Uniforms")[0]
    @property
    def IOPlaceHolder(self): return self.search_placeholder("IO")[0]
    @property
    def Includes(self): return self.search_placeholder("Includes")[0]
    @property
    def AfterIncludes(self): return self.search_placeholder("AfterIncludes")[0]
    @property
    def Defines(self): return self.search_placeholder("Defines")[0]


# Here is what all this jazz is about
class SombreroShaderMacros:
    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl

    def __default_placeholders_and_specification(self, shader):
        Version("330")(shader)
        PlaceHolder("IO")(shader)
        PlaceHolder("Defines")(shader)
        PlaceHolder("Mappings")(shader)
        PlaceHolder("Uniforms")(shader)
        for name in ["uniforms", "constants", "utils", "colors", "complex", "noise", "coordinates", "dynamic", "ray_marching"]:
            Include(Path(self.sombrero_mgl.sombrero_dir)/"glsl"/"include"/f"{name}.glsl")(shader)
        PlaceHolder("Includes")(shader)
        PlaceHolder("UserShader")(shader)
        PlaceHolder("AfterIncludes")(shader)

    # Versioned, placeholders, and sombrero specification
    def __base_shader(self) -> SombreroShader:
        with SombreroShader() as SHADER:
            self.__default_placeholders_and_specification(SHADER)

            # Return mainImage from main function, gamma correction of sqrt
            with Function("void", "main", "")(SHADER) as main:
                FragColor("mainImage(gl_FragCoord.xy)")(main)
        return SHADER

    # # These assign_to_parent are for automatically setting the parent SombreroMGL's .shader attribute
    # to what we will return. Using it False doesn't have much sense unless generating shaders from a single
    # macro instance then assigning to other SombreroMGLs

    # Load some fragment shader, vertex and geometry are defined per constructor object
    def load(self, path, assign_to_parent = True) -> SombreroShader:
        with self.__base_shader() as SHADER:
            Include(Path(path).resolve())(SHADER.UserShader)
        if assign_to_parent: self.sombrero_mgl.shader = SHADER; return
        return SHADER
    
    # def load(self, path, assign_to_parent = True) -> SombreroShader:
    #     with SombreroShader() as SHADER:
    #         Version("330")(SHADER)
    
    # Some shaders most likely pfx ones require one layer layer0, two layer0 layer1 to work this is 
    # so that you chain those, please read the shader you're loading first otherwise this might do nothing.
    def load_chain_dependent(self, path, processed_layers, assign_to_parent = True) -> SombreroShader:
        with self.__base_shader() as SHADER:
            self.__map_shader_as_textures(processed_layers, SHADER)
            Include(Path(path).resolve())(SHADER.UserShader)
        if assign_to_parent: self.sombrero_mgl.shader = SHADER; return
        return SHADER

    # # Map layers as shader textures layer0 layer1 layer2...
    def __map_shader_as_textures(self, layers, shader: SombreroShader):
        for index, layer in enumerate(layers):
            if hasattr(layer, "finish"): layer.finish()
            TextureShader(name = f"layer{index}", sombrero_mgl = layer)(shader, shader.Mappings, self.sombrero_mgl)

    def add_mapping(self, item): item(self.sombrero_mgl.shader, self.sombrero_mgl.shader.Mappings, self.sombrero_mgl)
    def add_include(self, item): item(self.sombrero_mgl.shader.Includes)

    # Alpha composite many layers together
    def alpha_composite(self, layers, gamma_correction = False, assign_to_parent = True, HUD = False, gamma_val = 2.0) -> SombreroShader:
        if HUD:
            hud = self.sombrero_mgl.new_child()
            hud.macros.load(self.sombrero_mgl.sombrero_dir/"glsl"/"default_hud.glsl")
            layers.append(hud)

        with self.__base_shader() as SHADER:
            self.__map_shader_as_textures(layers, SHADER)

            # mainImage function
            with Function("vec4", "mainImage", "in vec2 fragCoord")(SHADER.UserShader) as main:
                Variable("vec4", "col", "vec4(0.0)")(main)

                # Alpha composite every layer
                for index, layer in enumerate(layers):
                    # New, Old, Target -> Target = AC(New, Old)
                    AlphaComposite("col", Texture(f"layer{index}", "shadertoy_uv"), "col")(main)

                # Gamma correction
                if gamma_correction: GammaCorrection("col", "col", gamma_val)(main)
                Return("col")(main)
        if assign_to_parent: self.sombrero_mgl.shader = SHADER; return
        return SHADER
