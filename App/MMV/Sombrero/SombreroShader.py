"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

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

from MMV.Common.Utils import Utils

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

    # Search for some specific class instance like SearchClass(IO) will yield all the IOs
    def SearchClass(self, who): return [stuff for stuff in self.everyone if isinstance(stuff, who)]

    # If item has attribute name (functions, placeholders) then match against it
    def SearchByName(self, Name):
        return [Item for Item in self.everyone if ((hasattr(Item, "Name")) and (Item.Name == Name))]

    # Search some placeholder
    def SearchPlaceholder(self, Name):
        r = [Item for Item in self.SearchByName(Name) if isinstance(Item, PlaceHolder)]
        print("Search", Name, r)
        return r



# Build method will only yield each content being built to a plain list, we can override this though
class SimpleBuildableChilds:
    def Build(self, indent = "") -> list:
        return [built for item in self.contents for built in item.Build(indent = indent)]

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
    def Build(self, indent = "") -> list: return [f"#version {self.number}"]

class Define(CallableAddToParent):
    def __init__(self, what): self.what = what
    def Build(self, indent = "") -> list: return [f"#define {self.what}"]

class Include(CallableAddToParent):
    def __init__(self, file): self.file = file
    def Build(self, indent = "") -> list:
        data = Path(self.file).resolve().read_text()
        ret = [f"// // Include [{self.file}]\n"]
        for line in data.split("\n"):
            ret += [f"{indent}{line}"]
        ret += [f"\n// // End Include [{self.file}]"]
        return ret

# # Variables, Uniforms
class Uniform(CallableAddToParent):
    def __init__(self, var_type, Name, value = None): Utils.AssignLocals(locals())
    def Build(self, indent = "") -> list: return [f"{indent}uniform {self.var_type} {self.Name};"]
class Variable(CallableAddToParent):
    def __init__(self, var_type, Name, value): Utils.AssignLocals(locals())
    def Build(self, indent = "") -> list: return [f"{indent}{self.var_type} {self.Name} = {self.value};"]

# # Return stuff
class Return(CallableAddToParent):
    def __init__(self, what): self.what = what
    def Build(self, indent = "") -> list: return [f"{indent}return {self.what};"]
class FragColor(CallableAddToParent):
    def __init__(self, what): self.what = what
    def Build(self, indent = "") -> list: return [f"{indent}fragColor = {self.what};"]

# One input or output marked variable, communication between vertex, geometry and fragment shader
class IO(CallableAddToParent):
    def __repr__(self): return f"<IO {str(id(self))[-4:]} Name:\"{self.Name}\" mode:\"{self.mode}\">"
    def __init__(self, glsltype, Name, use = True, prefix = True, mode = "io", flat = False):
        Utils.AssignLocals(locals())
        {"io": self.do_input_and_output, 'i': self.do_only_input, 'o': self.do_only_output}.get(mode, "io")()

    def Build(self, indent = "") -> list:
        R = []
        prefix = "flat " if self.flat else ""
        if "i" in self.mode: R += [f"{indent}{prefix}in {self.glsltype} {self.InName};"]
        if "o" in self.mode: R += [f"{indent}{prefix}out {self.glsltype} {self.OutName};"]
        return R

    def do_only_input(self): self.mode = "i"
    def do_only_output(self): self.mode = "o"
    def do_input_and_output(self): self.mode = "io"

    @property
    def InName(self) -> str:
        if self.prefix: return f"in_{self.Name}"
        return f"{self.Name}"
    @property
    def OutName(self) -> str:
        if self.prefix: return f"out_{self.Name}"
        return f"{self.Name}"

# Alpha composite function from sombrero specification
class AlphaComposite(CallableAddToParent):
    def __init__(self, old, new, target): Utils.AssignLocals(locals())
    def Build(self, indent = "") -> list: return [f"{indent}{self.target} = mAlphaComposite({self.old}, {self.new});"]

class GammaCorrection(CallableAddToParent):
    def __init__(self, assign, who, gamma): Utils.AssignLocals(locals())
    def Build(self, indent = ""): return [f"{indent}{self.assign} = pow({self.who}, vec4(1.0 / {self.gamma}));"]
 
# Define something on your own!
class CustomLine(CallableAddToParent):
    def __init__(self, content): self.content = content
    def Build(self, indent = "") -> list: return [f"{indent}{self.content};"]

# Incomplete statement, meant to be used alongside some other one. They also return strings
# when called inside fstrings, makes sense since we want to just f"something {partialstatement}"
# and no need to directly call build on them
class PartialStatement:
    def __repr__(self): return self.build()

class Texture(PartialStatement):
    def __init__(self, sampler2D, uv): Utils.AssignLocals(locals())
    def Build(self, indent = "") -> str: return f"texture({self.sampler2D}, {self.uv})"


# # Scoped


class Function(WithScopedAddToParent):
    def __init__(self, return_type, Name, arguments):
        super().__init__(); Utils.AssignLocals(locals())

    def Build(self, indent = "") -> list:
        data = [f"{indent}{self.return_type} {self.Name}({self.arguments}) {{"]
        for item in self.contents:
            data += [f"{indent}{line}" for line in item.Build("    " + indent)]
        data += [f"{indent}}}"]
        return data


class PlaceHolder(Searchable, CallableAddToParent, SimpleBuildableChilds):
    def __repr__(self): return f"<PlaceHolder {str(id(self))[-4:]} \"{self.Name}\" {self.contents}>"
    def __init__(self, Name): super().__init__(); Utils.AssignLocals(locals())


# # Mappings


class GenericMapping:
    def __init__(self, **config): Utils.AssignLocals(locals())

    # We need where to place (parent =~= PlaceHolder), the main sombrero mgl and the shader
    def __call__(self, SombreroShader, parent, SombreroMain):
        Utils.AssignLocals(locals()); self.parent._add(self)

    # Return uniform type name;
    def Build(self, indent = ""):
        self.action()
        for item in self.info:
            if isinstance(item, Uniform):
                item( self.SombreroShader.Uniforms )
        return []

class TextureImage(GenericMapping):
    def action(self): self.info = self.SombreroMain.MapImage(**self.config)
class TextureShader(GenericMapping):
    def action(self): self.info = self.SombreroMain.MapShader(**self.config)
class TexturePipeline(GenericMapping):
    def action(self): self.info = self.SombreroMain.MapPipelineTexture(**self.config)


# # Main classes


# A Shader is basically a placeholder that have some inputs and outputs variables.
class SombreroShader(Searchable, SimpleBuildableChilds, SimpleEnterable):
    def __init__(self): super().__init__()
    def __repr__(self): return f"<Shader {self.contents}>"
    def copy(self): return copy.deepcopy(self)
    def Build(self, indent = "") -> str:
        return '\n'.join( [built for item in self.contents for built in item.Build(indent = indent)] )

    # Get In / Outs elements from the contents
    def GetIOs(self) -> list: return self.SearchClass(IO)

    @property
    def Mappings(self): return self.SearchPlaceholder("Mappings")[0]
    @property
    def UserShader(self): return self.SearchPlaceholder("UserShader")[0]
    @property
    def Uniforms(self): return self.SearchPlaceholder("Uniforms")[0]
    @property
    def IOPlaceHolder(self): return self.SearchPlaceholder("IO")[0]
    @property
    def Includes(self): return self.SearchPlaceholder("Includes")[0]
    @property
    def AfterIncludes(self): return self.SearchPlaceholder("AfterIncludes")[0]
    @property
    def Defines(self): return self.SearchPlaceholder("Defines")[0]


# Here is what all this jazz is about
class SombreroShaderMacros:
    def __init__(self, SombreroMain):
        self.SombreroMain = SombreroMain
        self.DefaultIncludes = [
            "Uniforms", "Constants", "Utils", "Colors", "Complex",
            "Noise", "Coordinates", "Dynamic", "RayMarching"]

    def __DefaultPlaceholdersAndSpecifications(self, Shader):
        Version("330")(Shader)
        PlaceHolder("IO")(Shader)
        PlaceHolder("Defines")(Shader)
        PlaceHolder("Mappings")(Shader)
        PlaceHolder("Uniforms")(Shader)
        for Name in self.DefaultIncludes:
            Include(Path(self.SombreroMain.PackageInterface.SombreroDir)/"Include"/f"{Name}.glsl")(Shader)
        PlaceHolder("Includes")(Shader)
        PlaceHolder("UserShader")(Shader)
        PlaceHolder("AfterIncludes")(Shader)

    # Versioned, placeholders, and sombrero specification
    def __BaseShader(self) -> SombreroShader:
        with SombreroShader() as SHADER:
            self.__DefaultPlaceholdersAndSpecifications(SHADER)

            # Return mainImage from main function, gamma correction of sqrt
            with Function("void", "main", "")(SHADER) as main:
                FragColor("mainImage(gl_FragCoord.xy)")(main)
        return SHADER

    # # These assign_to_parent are for automatically setting the parent SombreroMain's .shader attribute
    # to what we will return. Using it False doesn't have much sense unless generating shaders from a single
    # macro instance then assigning to other SombreroMains

    # Load some fragment shader, vertex and geometry are defined per constructor object
    def Load(self, path, AssignToParent=True) -> SombreroShader:
        with self.__BaseShader() as SHADER:
            Include(Path(path).resolve())(SHADER.UserShader)
        if AssignToParent: self.SombreroMain.Shader = SHADER; return
        return SHADER
    
    # def load(self, path, assign_to_parent = True) -> SombreroShader:
    #     with SombreroShader() as SHADER:
    #         Version("330")(SHADER)
    
    # Some shaders most likely pfx ones require one layer layer0, two layer0 layer1 to work this is 
    # so that you chain those, please read the shader you're loading first otherwise this might do nothing.
    def LoadChainDependent(self, path, processed_layers, assign_to_parent = True) -> SombreroShader:
        with self.__BaseShader() as SHADER:
            self.__MapShader_as_textures(processed_layers, SHADER)
            Include(Path(path).resolve())(SHADER.UserShader)
        if assign_to_parent: self.SombreroMain.shader = SHADER; return
        return SHADER

    # # Map layers as shader textures layer0 layer1 layer2...
    def __MapShader_as_textures(self, layers, shader: SombreroShader):
        for index, layer in enumerate(layers):
            if hasattr(layer, "finish"): layer.finish()
            TextureShader(name = f"layer{index}", SombreroMain = layer)(shader, shader.Mappings, self.SombreroMain)

    def AddMapping(self, item): item(self.SombreroMain.shader, self.SombreroMain.shader.Mappings, self.SombreroMain)
    def AddInclude(self, item): item(self.SombreroMain.shader.Includes)

    # Alpha composite many layers together
    def AlphaComposite(self, layers, gamma_correction = False, assign_to_parent = True, HUD = False, gamma_val = 2.0) -> SombreroShader:
        if HUD:
            hud = self.SombreroMain.NewChild()
            hud.macros.load(self.SombreroMain.SombreroDir/"DefaultHud.glsl")
            layers.append(hud)

        with self.__BaseShader() as SHADER:
            self.__MapShader_as_textures(layers, SHADER)

            # mainImage function
            with Function("vec4", "mainImage", "in vec2 fragCoord")(SHADER.UserShader) as main:
                Variable("vec4", "col", "vec4(0.0)")(main)

                # Alpha composite every layer
                for index, layer in enumerate(layers):
                    # New, Old, Target -> Target = AC(New, Old)
                    AlphaComposite("col", Texture(f"layer{index}", "ShaderToyUV"), "col")(main)

                # Gamma correction
                if gamma_correction: GammaCorrection("col", "col", gamma_val)(main)
                Return("col")(main)
        if assign_to_parent: self.SombreroMain.Shader = SHADER; return
        return SHADER
