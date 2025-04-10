# First, import the compatibility module to ensure it's available
from .py_compatibility import *

# Then import only the most critical modules for now
from .branch_info import __version__, BranchInfo
from .logs import logger
from .constants import MCDPConstants
from .dependencies import *
from .development import *