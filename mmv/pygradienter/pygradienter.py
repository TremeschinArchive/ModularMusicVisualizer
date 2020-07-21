"""
===============================================================================

Purpose: Main file to execute Gradienter

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

from processing import PyGradienterProcessing
from multiprocessing import Pool
from utils import Miscellaneous
from utils import Utils
import importlib.util
import argparse
import copy
import sys
import os


# Main class that controls PyGradienter
class PyGradienter():
    def __init__(self, args):

        # Get the args from the CLI interface
        self.args = args

        # Create Utils and get this file location
        self.utils = Utils()
        self.ROOT = self.utils.get_root()

        # Load the profiles.yaml file and get the profiles key
        self.config = self.utils.load_yaml(self.ROOT + os.path.sep + "settings.yaml")

        # List the files under the profiles directory that end with .py
        self.profiles = [x.replace(".py", "") for x in os.listdir(self.ROOT + os.path.sep + "profiles")]

        # If user run the program with a -l argument
        if self.args["list"]:
            print(" Available profiles from the profiles directory:")
            for item in sorted(os.listdir(self.ROOT + os.path.sep + "profiles")):
                if item.endswith(".py"):
                    f = importlib.import_module('profiles.' + item.replace(".py", ""))
                    print(" -", item.replace(".py", ""))
                    print("    >", f.description)

        # No profile chosen
        elif self.args["profile"] == None:
            print(" [ERROR] Please select an profile or see gradienter.py -h for help\n")

        # Run with a profile
        else:
            # Fail safe, user input is not a filename under profiles dir
            if not self.args["profile"] in self.profiles:
                print(" [ERROR] No profile found for [%s] under profiles.yaml\n" % self.args["profile"])
                sys.exit(-1)

            # Change the settings on config based on arguments
            if not self.args["number"] == None:
                self.config["generate_n_images"] = int(self.args["number"])

            if not self.args["width"] == None:
                self.config["width"] = int(self.args["width"])

            if not self.args["height"] == None:
                self.config["height"] = int(self.args["height"])
            
            if self.args["quiet"]:
                self.config["quiet"] = True
            else:
                self.config["quiet"] = False
            
            if self.args["delete"]:
                self.utils.rmdir(self.ROOT + os.path.sep + "data")

            # Import the module (profile file) for multiprocessing
            self.profile = importlib.import_module('profiles.' + self.args["profile"])

            # Create pool
            pool = Pool()

            # Start up the profile
            profile = self.profile.PyGradienterProfile(self.config)
            profile.id = 0

            # List for mapping multiprocess
            data_inputs = []

            # Create the lists on how many images we'll create
            for _ in range(self.config["generate_n_images"]):

                # Add one ID for generating different random seeds
                profile.id += 1

                # Add a copy of the object as a argument            
                data_inputs.append(
                    copy.deepcopy(profile)
                )

            # Main routine on making the images, multiprocessing these
            pool.map(PyGradienterProcessing, data_inputs)

            pool.close()


if __name__ == "__main__":

    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Arguments for PyGradienter')

    # Add arguments
    args.add_argument('-l', '--list', required=False, action="store_true", help="(solo) Lists available profiles on profiles.yaml")
    args.add_argument("-p", "--profile", required=False, help="(string) Generate gradient images with this profile")
    args.add_argument("-n", "--number", required=False, help="(int) Override settings on number images to generate")
    args.add_argument("-x", "--width", required=False, help="(int) Override width setting on file")
    args.add_argument("-y", "--height", required=False, help="(int) Override height setting on file")
    args.add_argument("-q", "--quiet", required=False, action="store_true", help="(solo) Quiet mode, only prints profile being generated")
    args.add_argument("-d", "--delete", required=False, action="store_true", help="(solo) Delete data folder before generating images")

    # Parse and organize the arguments
    args = args.parse_args()
    args = {
        "list": args.list,
        "profile": args.profile,
        "number": args.number,
        "width": args.width,
        "height": args.height,
        "quiet": args.quiet,
        "delete": args.delete,
    }

    # Greeter message :)
    # Or not :(
    if not args["quiet"]:
        Miscellaneous()

    # Run the main class with the args
    PyGradienter(args)
