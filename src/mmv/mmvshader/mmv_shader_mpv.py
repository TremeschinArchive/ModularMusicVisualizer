"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Utility to wrap around mpv and add processing shaders, target
resolutions, input / output

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH, STEP_SEPARATOR
import subprocess
import logging
import shutil
import sys
import os


class MMVShaderMPV:
    def __init__(self, main, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_main = main

        # Create empty config
        self.reset()

    # Reset configured stuff
    def reset(self, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.reset]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Resetting MMVShaderMPV to empty configuration")

        # List of shaders to apply
        self.shaders = []

        # Where and what to load, output
        self.input_video = ""
        self.output_video = ""

        # Default resolution / fps values
        self.width = 1280
        self.height = 720
        self.fps = None  # None means use the input's fps

        # # Final command to run, start with the mpv executable

        # Linux and MacOS don't use suffixes
        mpv_binary = "mpv"

        # On Windows look for an .exe extensions
        if (self.mmv_main.utils.os == "windows"):
            mpv_binary += ".exe"
        
        # Try finding mpv binary
        logging.info(f"{depth}{debug_prefix} Getting mpv binary [{mpv_binary}] path..")
        mpv_binary_path = self.mmv_main.utils.get_executable_with_name(mpv_binary)

        # get_executable_with_name returns False if it's not found, up for who
        # uses the function to handle errors so here we are
        if not mpv_binary_path:
            raise RuntimeError(f"Could not find mpv binary named [{mpv_binary}] on the system.")

        logging.info(f"{depth}{debug_prefix} mpv binary path is [{mpv_binary_path}]")

        # Start with the mpv binary
        self.__command = [mpv_binary_path]

        # Blank x264 settings
        self.x264_flags = []
        logging.info(f"{depth}{debug_prefix} Resetting to default x264 settings")
        self.x264_settings()

        logging.info(f"{depth}{debug_prefix} Done!!")

        logging.info(STEP_SEPARATOR)

    # # Internal functions

    # Generate the final command to run
    def __generate_command(self, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.__generate_command]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Generating run command")
        
        # Preliminary error assertion
        assert (not self.input_video == ""), "No input video specified"

        # Add input source
        self.__command += [self.input_video]
        logging.info(f"{depth}{debug_prefix} Added input video [{self.input_video}] to command")

        # # Append shaders flags for every shader we added

        # If we do have at least one shader, add --glsl-shader=path for every shader path
        if self.shaders:

            # Assert that every shader is a valid file on the disk
            assert (any([os.path.isfile(path) for path in self.shaders]))
            logging.info(f"{depth}{debug_prefix} All shaders given are existing files on the disk")

            # # For every shader add its flag
            
            logging.info(f"{depth}{debug_prefix} Adding all shaders to command:")            
            
            # Iterate over shaders
            for shader in self.shaders:

                # Generate the flag and append it
                flag = f"--glsl-shader={shader}"
                self.__command.append(flag)

                # Pretty print
                logging.info(f"{depth}{debug_prefix} -> [{flag}]")            

        # If we have some output video, render to it, otherwise display realtime (no -o flag)
        if self.output_video is not None:
            logging.info(f"{depth}{debug_prefix} Output video is not None, render to file [{self.output_video}]")       

            # https://github.com/mpv-player/mpv/issues/7193#issuecomment-559898238
            if self.mmv_main.os == "windows":
                spacer = "-" * shutil.get_terminal_size()[0]
                raise RuntimeError((
                    f"\n\n{spacer}\n"
                    "\n  # # [ ERROR ] # #\n\n"
                    "Current implementation for rendering shaders to videos is simply not possible on Windows due mpv limitations..\n"
                    "See comment https://github.com/mpv-player/mpv/issues/7193#issuecomment-559898238\n\n"
                    "You can however visualize the final output and perhaps record the screen but quality will be bad.\n"
                    "You can consider:\n"
                    " - Installing an Linux distro on spare HDD and running MMV there.\n"
                    " - Help fixing this (recommending other ways to render the shaders).\n"
                    " - Wait until it's doable rendering to video on Windows OS.\n"
                    f"\n{spacer}\n"
                    "I really wanted it to work there properly but this --vf=gpu flag is experimental anyways, I should be expecting those\n"
                ))

            # Render on the GPU with the specified width and height
            self.__command.append(f'--vf=gpu=w={self.width}:h={self.height}')

            # Add flag asking mpv to render to a file
            self.__command += ["-o", self.output_video]
        
        # Add x264 flags
        logging.info(f"{depth}{debug_prefix} Appending libx264 encoding flags:")            
        for flag in self.x264_flags:
            self.__command.append(flag)
            logging.info(f"{depth}{debug_prefix} > [{flag}]")            

        # Print full command and we're done, just need to execute it
        logging.info(f"{depth}{debug_prefix} Full command is {self.__command}")
        logging.info(STEP_SEPARATOR)

    # # Interface, end user functions

    # Adds a new shader as processing layer to the final video
    def add_shader(self, shader_path, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.add_shader]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Get absolute path always
        shader_path = self.mmv_main.utils.get_abspath(shader_path)
        logging.info(f"{depth}{debug_prefix} Add shader with path: [{shader_path}]")

        # Assign values
        self.shaders.append(shader_path)
        logging.info(STEP_SEPARATOR)

    # Configure x264 encoding flags like crf, preset, audio codec and bitrate
    def x264_settings(self, audio_codec = "libopus", audio_bitrate = 300000, crf = 18, preset = "fast", depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.x264_settings]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Set new x264 flags
        self.x264_flags = [
            f"--oac={audio_codec}", f"--oacopts=b={audio_bitrate}",
            "--ovc=libx264", f"--ovcopts=preset={preset}", f"--ovcopts=crf={crf}"
        ]

        logging.info(f"{depth}{debug_prefix} x264 flags: {self.x264_flags}")
        logging.info(STEP_SEPARATOR)

    # Configure input and output, if output is None that means don't render, only display real time
    def input_output(self, input_video, output_video = None, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.input_output]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Get absolute path always
        input_video = self.mmv_main.utils.get_abspath(input_video)
        if output_video is not None:
            output_video = self.mmv_main.utils.get_abspath(output_video)

        # Warn info
        logging.info(f"{depth}{debug_prefix} Set input video: [{input_video}]")
        logging.info(f"{depth}{debug_prefix} Set output video: [{output_video}]")

        # Assign values
        self.input_video = input_video
        self.output_video = output_video
        logging.info(STEP_SEPARATOR)
    
    # Configure the resolution width, height to render
    def resolution(self, width, height, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.resolution]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Warn info
        logging.info(f"{depth}{debug_prefix} Set resolution width: [{width}]")
        logging.info(f"{depth}{debug_prefix} Set resolution height: [{height}]")

        # Assign values
        self.width = width
        self.height = height
        logging.info(STEP_SEPARATOR)
        
    # Execute this class with the stuff configured
    def run(self, execute = True, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMPV.run]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        logging.info(f"{depth}{debug_prefix} Generate command then run!")

        # Generate command
        self.__generate_command()

        if self.mmv_main.prelude["flow"]["stop_at_run_command"]:
            logging.critical(f"{depth}{debug_prefix} Stopping program as key stop_at_run_command is True on prelude.toml")
            sys.exit(0)
            
        # If we just wanna see the final command, don't execute
        if execute:
            logging.info(f"{depth}{debug_prefix} Starting mpv subprocess with self.__command list, here be dragons..")
            subprocess.run(self.__command)

