import sys
import os

# Append previous folder to path
sys.path.append("..")
sys.path.append(
    os.path.dirname(os.path.abspath(__file__)) + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVInterface()

# Testing
interface.download_check_ffmpeg(making_release = True)
interface.download_check_mpv(making_release = True)
interface.download_check_musescore(making_release = True)
