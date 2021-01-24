import sys
import os

# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()

comment = {
    "ffmpeg": "It should work as expected, downloads and extracts to the externals folder",
    "mpv": "It should work as expected, downloads and extracts to the externals folder",
    "musescore": "It should work as expected, downloads and extracts to the externals folder",
}

# Testing
for external in ["ffmpeg", "mpv", "musescore"]:
    c = comment[external]
    print(f"\n{c}\n")
    interface.check_download_externals(target_externals = external)
