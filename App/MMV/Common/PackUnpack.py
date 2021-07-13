"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Save compressed Python objects to file, load them

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
import os
import pickle
import sys
import zlib
from pathlib import Path


class PackUnpack:

    # Pack a Python object to a file, pickle it first then compress using
    # zlib for some semi-free space optimization. Recommended file "extension"
    # is .pickle.zlib
    @staticmethod
    def Pack(data, path) -> None:
        p = Path(path).resolve()
        logging.info(f"[PackUnpack.Unpack] Packing to file [{data}] => [{p}]")
        data = pickle.dumps(data)
        old, data = data, zlib.compress(data, level=9)
        oldb, newb = sys.getsizeof(old), sys.getsizeof(data)
        logging.info(f"[PackUnpack.Pack] Pack [{p}] Compression ratio [{(oldb/newb):.3f}] [{oldb} bytes -> {newb} bytes]")
        Path(path).write_bytes(data)

    # Unpack a object from a python file given the file written from the function above.
    @staticmethod
    def Unpack(path) -> object:
        p = Path(path).resolve()
        logging.info(f"[PackUnpack.Unpack] Unpacking file [{p}]")
        data = pickle.loads(zlib.decompress(p.read_bytes()))
        logging.info(f"[PackUnpack.Unpack] Unpacked file [{p}]")
        return data
