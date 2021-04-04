"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Abstraction on BlockOfCode class

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
import uuid
import copy


# Abstraction on scoped and "linearly independent" snippets of code
# we can keep adding on a shader file
class BlockOfCode:
    VERBOSE = False
    NEWLINE_PREVIOUS_AND_AFTER = True

    # Start either with nothing, some lines. This argument can be string or list,
    # will be converter to 1 element list if string and delete every \n
    # Pretty writes delimiters for each block of code so they are easily "viewable"
    def __init__(self, some_starting_lines = [], scoped = True, name = None, pretty = True):
        self.__enabled = True
        self.__scoped = scoped
        self.__pretty = pretty
        self.lines = []

        self.__name = str(uuid.uuid4())[1:6] if (name is None) else name

        # Enforce list
        if not isinstance(some_starting_lines, list):
            some_starting_lines = some_starting_lines.split("\n")

        # If we do have some init stuff
        for line in some_starting_lines:
            self.add_line(line.replace("\n", ""))

    # Utils
    def scope(self): self.__scoped = True
    def unscope(self): self.__scoped = False

    def pretty(self): self.__pretty = True
    def unpretty(self): self.__pretty = False

    def set_name(self, name): self.__name = name
    def get_name(self): return self.__name

    def disable(self): self.__enabled = False
    def enable(self): self.__enabled = True

    def clone(self): return copy.deepcopy(self)

    # Add a line to this instance
    def add_line(self, data):
        if BlockOfCode.VERBOSE: logging.info(f"[BlockOfCode.add_line] [{data}]")
        self.lines.append(data)
    
    # Add some other block of code to the lines
    def extend(self, extension):
        extension.set_name(f"{extension.get_name()} [Extends: {self.__name}]")
        for line in extension.get_content():
            self.add_line(line.replace("\n", ""))
    
    # Return the lines as a string
    # Scoped yields the string surrounded by {} and properly indented
    def get_content(self, indent = "", newline = True) -> list:

        # Start empty
        content = []
        nested_indentations = ""
        nested_extra_indent = "    " if self.__scoped else ""
        namestr = f"// BlockOfCode: [{self.__name}]"

        # For every item on the lines
        for item in self.lines:

            # If item is another BlockOfCode element, we get its content and add
            # its lines before continuing. This is the recursive part of this class
            if isinstance(item, BlockOfCode):
                for subcontent in item.get_content(indent = nested_indentations + "    "):
                    content.append(subcontent)
            
            else: # It's just some string from this instance, keep adding it
                t = f"{nested_extra_indent}{item}\n"
                content.append(t)

        # Scope the code
        if self.__scoped:
            content.insert(0, f"{{ {namestr}\n")
            content.append(f"}}; {namestr}\n")
        else:
            content.insert(0, f"{namestr}\n")
            content.append(f"{namestr}\n")
        
        # Add delimiters
        if self.__pretty:
            max_height = max([len(stuff) for stuff in content])

            for index, data in enumerate(content):
                whitespace = " "
                if (index == 0) or (index == len(content) - 1):
                    whitespace = "-"
                content[index] = data.replace("\n", "") + whitespace * (max_height - len(data) + 2) + "//\n"

        # Log if verbose, either way return content with added final indent
        if BlockOfCode.VERBOSE: logging.info(f"[BlockOfCode.get_content] Return content [{content}]")
        constructed = []

        # Comment everything or not
        enabled = "" if self.__enabled else "// "

        # Add new line spacing between block of codes
        for index, line in enumerate(content):
            if BlockOfCode.NEWLINE_PREVIOUS_AND_AFTER and (index == 0) and self.__pretty: constructed.append("\n")
            constructed.append(f"{indent}{enabled}{line}")
            if BlockOfCode.NEWLINE_PREVIOUS_AND_AFTER and (index == len(content) - 1) and self.__pretty: constructed.append("\n")

        # Remove newline
        if not newline:
            constructed = [l.replace("\n", "") for l in constructed]

        return constructed
        
    # Get string representation of the content
    def get_string_content(self, indent = "") -> str: return ''.join(self.get_content(indent = indent))

    def __str__(self):
        print("\n[BlockOfCode.__str__] <><><><><> Show representation of string <><><><><>")
        for i, line in enumerate(self.get_content()):
            print(f"[{i:04}] | {line}", end = '')
        return ""
