"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Get / set values to this class, automatically saves to disk

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
from pathlib import Path
import ujson as json
import logging


class PersistentDictionary:
    def __init__(self, path: Path):
        debug_prefix = "[PersistentDictionary.__init__]"
        logging.info(f"{debug_prefix} Create class, path [{path}]")
        self.__path = Path(path).resolve()
        self.__dictionary = {}
        self.__defaults = {}
        self.__load()

    # TODO: Pickle than json?
    
    def __load(self) -> None:
        if not self.__path.is_file:
            self.__dictionary = json.loads(self.__path.read_text("utf-8"))
    
    def __save(self) -> None:
        self.__path.write_text(json.dumps(self.__dictionary))

    @property
    def path(self) -> Path:
        return self.__path
    
    @property
    def contents(self) -> dict:
        return self.__dictionary
    
    def set_defaults(self, defaults: dict) -> None:
        self.__defaults = defaults

    def get(self, name):
        debug_prefix = "[PersistentDictionary.get]"

        # Name is in dictionary
        if name in self.__dictionary.keys(): 
            logging.info(f"{debug_prefix} Get key [{name}]")
            return self.__dictionary[name]  
        
        # Name not in dictionary
        logging.warning(f"{debug_prefix} Key [{name}] not in dictionary, returning default key if exist")
        return defaults[name]

    def set(self, name, value):
        debug_prefix = "[PersistentDictionary.set]"
        logging.warning(f"{debug_prefix} Set key [{name}] to [{value}], save to file")
        self.__dictionary[name] = value
        self.__save()


if __name__ == "__main__":
    d = PersistentDictionary("./test.json")
    d.get("something")
    d.set("abc", "yes")