# Suppress NumPy warning about weird divisions, mean of empty slice
# Or numpy-quaternions package saying to use Numba which we're not
# computing big big matrices of vectors to rotate..
import warnings
warnings.filterwarnings("ignore")

# Hide PyGame intro message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Nuitka "Missing imports"
import glfw

# Import PackageInterface that controls the whole MMV
from MMV.PackageInterface import mmvPackageInterface
