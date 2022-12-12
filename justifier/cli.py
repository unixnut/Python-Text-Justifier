"""Console script for justifier."""

from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import sys
import logging

import click

from justifier import init_logging, params, __version__   # This package's top-level module
from justifier import justifier


@click.command(help="Input to justify")
@click.option("--width", "-w", type=int, help="Width of text, not counting indent")
@click.option("--indent", "-i", type=int, help="Number of spaces to add before text")
@click.option("--right-margin", "-i", type=int, help="Indent plus width")
@click.option("--simple-hyphen", "-s", 'hyphenation', flag_value='simple', help="Hyphenation method")
@click.option("--hyphen", "-h",        'hyphenation', flag_value='pyphen', default=True, help="Hyphenation method")
@click.option("--no-hyphenate", "-H",  'hyphenation', flag_value='none', help="Turn hyphenation off")
@click.option("--debug/--no-debug", "-d", default=False, help="Turn on debug mode")
@click.argument("input", type=click.File(), default="-")
def main(input: TextIO, width: Optional[int], indent: Optional[int], right_margin: Optional[int], hyphenation: str, debug: bool):
    """Console script for justifier."""

    master_logger = init_logging(loglevel=(debug and logging.DEBUG or logging.WARNING))

    indent = 0
    if width:
        params['right_margin'] = width + indent

    params['hyphenation'] = hyphenation

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
