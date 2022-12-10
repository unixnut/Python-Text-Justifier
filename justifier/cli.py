"""Console script for justifier."""

from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import sys
import logging

import click

from justifier import init_logging, params, __version__   # This package's top-level module
from justifier import justifier


@click.command(help="Input to justify")
@click.option("--width", "-w", type=int, help="Width of text, not counting indent")
@click.option("--debug/--no-debug", "-d", help="Turn on debug mode")
@click.argument("input", type=click.File(), default="-")
def main(input: TextIO, width: Optional[int], debug: bool = False):
    """Console script for justifier."""

    master_logger = init_logging(loglevel=(debug and logging.DEBUG or logging.WARNING))
    
    indent = 0
    if width:
        params['right_margin'] = width + indent

    justifier.init(master_logger)
    justifier.process(input)
    ## for line in input:
    ##     print(line)
    ##     break
    justifier.finalise()

    ## click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
