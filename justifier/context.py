"""
Handles environment variables, config files, UI, etc.
"""

from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import os


# *** DEFINITIONS ***
DEFAULT_COLUMNS = 80


# *** FUNCTIONS ***
def screen_width() -> int:
    # Note: `os.getenv('COLUMNS', DEFAULT_COLUMNS)` doesn't work normally, only
    # if $COLUMNS has been set in the environment explicitly, which the shell
    # doesn't do, so use an ioctl(2) call to query the pty driver
    try:
        info = os.get_terminal_size()
        num_columns = info.columns
        ## print(type(num_columns))
    except OSError:
        num_columns = int(os.getenv('COLUMNS', DEFAULT_COLUMNS))

    return num_columns
