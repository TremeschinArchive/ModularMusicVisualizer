

from playsound import playsound
from enum import Enum
import numpy as np
import samplerate
import threading
import datetime
import librosa
import shelve
import scipy
import math
import time
import os

# A point on the plot
class NamedPoint:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name


# Enum for common samples trickery for categorizing them
class SampleInfo(Enum):
    TOO_LONG = 1
    TOO_SHORT = 2
    NOT_FOUND = 3


class SampleSorter:
    """
    kwargs: {
        "path": list
            list of pathes to search recursively for samples
    }
    """
    def __init__(self, mmv, **kwargs):
        self.mmv = mmv

        import aubio
        import matplotlib.pyplot as plt
        self.samples = []

        # Get list of pathes for searching
        search_paths = self.mmv.utils.force_list(kwargs["path"])
        search_paths = [self.mmv.utils.get_abspath(path) for path in search_paths]

        self.NOT_A_SAMPLE_IF_DURATION_GREATER_THAN = 6
        self.WHO_IS_AUDIO = [".wav", ".ogg", ".flac", ".mp3"]
        self.THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ALGORITHM_VERSION = 1

        self.shelve_file = self.THIS_FILE_DIR + os.path.sep + "data.shelf"
        self.log_file = self.THIS_FILE_DIR + os.path.sep + "log.txt"

        # Constants
        self.win_size = 4096 
        self.hop_size = 512
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("")

        with shelve.open(self.shelve_file, 'c') as shelf:

            # # Cleanup and check file path entries, older entries, files that doesn't exist

            for file_path in shelf.keys():
                path = os.path.realpath(os.path.abspath(file_path))
                data = shelf[file_path]

                if not os.path.exists(path):
                    print(f"File path doesn't exist, deleting on shelf dictionary [{path}]")
                    del shelf[path]
                
                if "algorithm_version" in data.keys():
                    # Algorithm version has changed
                    if not data["algorithm_version"] == self.ALGORITHM_VERSION:
                        print(f"Algorithm version changed, deleting old entry [{path}]")
                        del shelf[path]
                else:
                    print(f"No algorithm version found, deleting entry [{path}]")
                    del shelf[path]

                # File was blocked
                if "blocked" in data:
                    if data["blocked"] == "too_long":
                        # Limits of greater than has changed
                        if not self.NOT_A_SAMPLE_IF_DURATION_GREATER_THAN == data["value"]:
                            print(f"Limits of minimum sample duration changed, deleting blocked entry [{path}]")
                            del shelf[path]

            # # Get processing files

            # For each path the user gave us for searching
            for path in search_paths:

                # Get all file paths to process
                files_to_process = []

                # Walk recursively on the path
                for root, dirs, files in os.walk(path):

                    # For each file in this folder, not including directories
                    for file in files:

                        # File is valid and will be listed for processing
                        if any([file.endswith(extension) for extension in self.WHO_IS_AUDIO]):
                            files_to_process.append(os.path.join(root, file))
                
                # Total number of file
                N_files = len(files_to_process)

                for index, file_path in enumerate(sorted(files_to_process)):
                    
                    # Check if file already been processed or new
                    if not file_path in shelf.keys():

                        print(f"Processing file [{index+1}/{N_files} : {((index+1)/N_files)*100:.2f}%] [{file_path}]")

                        # Process the file
                        info = self.process_file(file_path, print_info = True)

                        # Audio file is too long, perhaps a loop or big FX?
                        if info == SampleInfo.TOO_LONG:
                            shelf[file_path] = {
                                "blocked": "too_long",
                                "value": self.NOT_A_SAMPLE_IF_DURATION_GREATER_THAN,
                            }
                            print(" > Too long, not a sample\n")
                            self.write_log(f"File too long, not a sample [{file_path}]")
                            continue
                        
                        # Audio file is too short, couldn't even slice into self.hop_size
                        elif info == SampleInfo.TOO_SHORT:
                            shelf[file_path] = {
                                "blocked": "too_short",
                                "less_than": self.hop_size,
                            }
                            print(" > Too short, not a sample\n")
                            self.write_log(f"File too short, not a sample [{file_path}]")
                            continue

                        elif info == SampleInfo.NOT_FOUND:
                            shelf[file_path] = {
                                "blocked": "not_found",
                            }
                            print(" > Not found\n")
                            continue

                        # Sample is a valid sample
                        else:

                            # Guess the type..
                            sample_type = self.guess_sample_type(info)
                            info["sample_type"] = sample_type

                            print("Sample type is", sample_type)
                            
                            # Add the info to the file
                            shelf[file_path] = info

                            color = self.get_color_by_type(info["sample_type"])

                            # Add to plot points
                            self.samples.append(
                                NamedPoint(
                                    info
                                    ["standard_deviation"]**0.5,
                                    # ["duration"],
                                    info["dominant_frequency"],
                                    color,
                                    file_path
                                )
                            )
                    
                    # File is a valid sample and was already processed,
                    else:
                        # Get the previously processed info
                        info = shelf[file_path]

                        if "blocked" in info.keys():
                            print(f"Skipping file [{index+1}/{N_files} : {((index+1)/N_files)*100:.2f}%] [{file_path}] blocked")

                        else:
                            color = self.get_color_by_type(info["sample_type"])
                            
                            self.samples.append(
                                NamedPoint(
                                    info["standard_deviation"]**0.5,
                                    # ["duration"],
                                    info["dominant_frequency"],
                                    color,
                                    file_path
                                )
                            )

                            print(f"Skipping file [{index+1}/{N_files} : {((index+1)/N_files)*100:.2f}%] [{file_path}] already in shelve dictionary")
        self.plot()


    def process_file(self, path, print_info = False):

        # Load the file, get stereo and mono data, samplerate
        try:
            stereo_data, sample_rate = librosa.load(path, mono=False, sr=None)
        except FileNotFoundError:
            self.write_log(f"File not found [{path}]\n")
            return SampleInfo.NOT_FOUND

        channels = stereo_data.shape[0]

        # Get the mono data for processing
        if channels == 2:
            mono_data = (stereo_data[0] + stereo_data[1]) / 2
        else:
            mono_data = stereo_data

        # Trim the data of the file, we process only the mono for now
        # Normalize to 1 the mono_data
        mono_data = np.trim_zeros(mono_data)
        mono_data = mono_data / np.linalg.norm(mono_data)

        # Total number of samples points
        N_samples = mono_data.shape[0]

        # Info on duration, channels
        duration = N_samples / sample_rate

        # Audio is too long
        if duration > self.NOT_A_SAMPLE_IF_DURATION_GREATER_THAN:
            return SampleInfo.TOO_LONG

        # Higher standard deviation should mean a higher quantity of bass but also can define a bit of punchiness?
        standard_deviation = np.std(mono_data)

        # # Dominant frequency

        pitch_o = aubio.pitch("yin", self.win_size, self.hop_size, sample_rate)
        # pitch_o.set_unit("midi")
        pitch_o.set_tolerance(0.8)

        pitches = []
        confidences = []

        data = np.zeros(math.ceil(N_samples / self.hop_size) * self.hop_size, dtype = "float32")
        data[0:N_samples] = mono_data
        N_chunks = (data.shape[0] / self.hop_size)
        
        if int(N_chunks) == 0:
            return SampleInfo.TOO_SHORT

        chunks = np.split(data, N_chunks)

        # For each chunk of processed stuff
        for chunk in chunks:

            # We're probably on the last chunk and it will potentially be less than self.hop_size
            if not len(chunk) == self.hop_size:
                break

            # Get pitch, confidence
            pitch = pitch_o(chunk)[0]
            confidence = pitch_o.get_confidence()

            # Append to the lists
            pitches += [pitch]
            confidences += [confidence]
        
        # Couldn't read even one hop_size, sample too short
        if len(pitches) + len(confidences) == 0:
            return SampleInfo.TOO_SHORT

        # Dominant frequency is the weighted averages of the pitches and confidences of aubio
        dominant_frequency = sum( [confidences[i] * pitches[i] for i in range(len(pitches))] ) / sum(confidences)
        
        if print_info:
            pretty_print = " ::"
            # print(pretty_print, f"Path:               [\"{path}\"]")
            print(pretty_print, f"Channels:           [{channels}]")
            print(pretty_print, f"Duration:           [{duration:.2f}]")
            print(pretty_print, f"Standard deviation: [{standard_deviation:.16f}]")
            print(pretty_print, f"Dominant Freq:      [{dominant_frequency:.2f}]")
            print()

        return {
            "path": path,
            "duration": duration,
            "standard_deviation": standard_deviation,
            "dominant_frequency": dominant_frequency,
            "algorithm_version": self.ALGORITHM_VERSION,
        }

    # Guess the sample type..
    def guess_sample_type(self, info):

        mode = "cheap"

        # Guess by the path.. not really good but welp
        if mode == "cheap":

            file_name = info["path"].split(os.path.sep)[-1].lower()

            if any([keyword in file_name for keyword in ["snare"]]):
                return "snare"
            
            if any([keyword in file_name for keyword in ["kick"]]):
                return "kick"
            
            if any([keyword in file_name for keyword in ["tom"]]):
                return "tom"
            
            if any([keyword in file_name for keyword in ["perc"]]):
                return "percussion"
            
            if any([keyword in file_name for keyword in ["hat"]]):
                return "hat"

            if any([keyword in file_name for keyword in ["ride"]]):
                return "ride"

    def get_color_by_type(self, sample_type):
        return {
            "snare": "m",
            "kick": "k",
            "tom": "c",
            "percussion": "g",
            "hat": "y",
            "ride": "b"
        }.get(sample_type, "r")

    # Write to the log file
    def write_log(self, string):
        now = datetime.datetime.now()
        date_and_time = now.strftime("%d/%m/%Y %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{date_and_time} {string}")

    def plot(self):
        fig, ax = plt.subplots()
        ax.set_yscale('log')

        for obj in self.samples:
            print(obj.color)
            artist = ax.plot(obj.x, obj.y, obj.color + 'o', picker=5)[0]
            artist.obj = obj

        fig.canvas.callbacks.connect('pick_event', self.clicked_sample)

        plt.show()

    def clicked_sample(self, event):
        who = event.artist.obj.name
        print(who)
        
        threading.Thread(target=playsound, args=(who,)).start()




    def resample(self,
            data: np.ndarray,
            original_sample_rate: int,
            new_sample_rate: int
        ) -> None:

        ratio = new_sample_rate / original_sample_rate
        if ratio == 1:
            return data
        else:
            return samplerate.resample(data, ratio, 'sinc_best')

    # We have two points P1 = (Xa, Ya) and P2 = (Xb, Yb)
    # It forms a line and we get a value of that line at X=get_x
    def value_on_line_of_two_points(self, Xa, Ya, Xb, Yb, get_x):
        # The slope is m = (Yb - Ya) / (Xb - Xa)
        # Starting from point Yb, we have Y - Yb = m(X - Xb)
        # so.. Y - Yb = ((Yb - Ya) / (Xb - Xa))(X - Xb)
        # And we want to isolate Y -->
        # Y = ((Yb - Ya) / (Xb - Xa))*(X - Xb) + Yb
        return ((Yb - Ya) / (Xb - Xa))*(get_x - Xb) + Yb
