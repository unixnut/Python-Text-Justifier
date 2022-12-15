"""Main module."""

from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import re
import logging
from collections import namedtuple
import random
import locale

import pyphen

import justifier   # This package's top-level module
from . import utils


# *** DEFINITIONS ***
logger = None   # logging.Logger
pyphen_hyphenator = None   # pyphen.Pyphen
p = None  # Pipeline


# *** CLASSES ***
Chunk = namedtuple('Chunk', ['word', 'sep'])




# *** FUNCTIONS ***
def get_paras(dest: Generator):
    """
    Coroutine that chunks lines into paragraphs
    @p dest: Next generator object
    """

    logger.debug("get_paras started; %s", repr(dest))

    try:
        data = None
        while True:
            ## logger.debug("getting...")
            line = yield
            ## logger.debug("got %d chars", len(line))
            if line:
                if data is not None:
                    data += " " + line
                else:
                    data = line
            else:
                # A blank line sends the collected paragraphs, if any
                if data is not None:
                    dest.send(data)
                    data = None

    except GeneratorExit:
        pass

    finally:
        # Send the final collected paragraph, if any
        if data is not None:
            dest.send(data)


def reformat(dest: Generator):
    """
    Receive a series of paragraphs and use a pair of create_folded_para() and
    collate_lines() generators to handle each one.
    """

    def chunk_to_words(s: str, dest: Union[Generator, utils.Pipeline]):
        logger.debug("chunk_to_words started; %s", repr(dest))

        # Do we need to chop the last separator?
        for match in reo.finditer(para):
            if match:
                chunk = (match.group(1), match.group(2) or "")
            else:
                chunk = ("", "")
            dest.send(chunk)


    # -- reformat() --
    sep_regex = justifier.params.get('sep_regex', r"\s")
    reo = re.compile("((?:(?!%s).)+)((?:%s)*)" % (sep_regex, sep_regex))
    try:
        while True:
            para = yield
            ## logger.debug(para)

            # Fan-in to this generator's `dest`
            coll = collate_lines(dest)
            coll.send(None)

            # Create a mini-pipeline just for this paragraph
            # (entities are created in reverse order)
            if justifier.params.get('indent') > 0:
                p = utils.Pipeline(create_folded_para,
                                   (indent_lines, {'indent': justifier.params['indent']}),
                                   coll)
            else:
                p = utils.Pipeline(create_folded_para, coll)

            # Run the mini-pipeline
            chunk_to_words(para, p)

            # Clean up the mini-pipeline in forwards order
            p.close()

    except GeneratorExit:
        pass


def create_folded_para(dest: Generator):
    """
    Coroutine that formats a series of words into a paragraph.
    @p dest: Next generator object

    @warning Not a main-chain generator, so do NOT close `dest`.
    """

    def line_render(a: List[Chunk]) -> str:
        """
        Join all chunks (word and separator) together into a line, without the
        last separator.
        """

        # Remove the spaces after the final word, if any
        if a[-1].sep:
            new_chunk = Chunk(a[-1].word, "")

        return "".join(c.word + c.sep for c in a)


    def simple_hypenate(word: str, delta: int) -> Tuple[str, str]:
        lfragment = word
        rfragment = ""

        # Reduce the lfragment length by one each iteration
        while len(lfragment) > delta:
            lfragment = word[0:len(lfragment)-2] + "-"
            rfragment = word[len(lfragment)-1:]   # len(lfragment) changed prev line
        logger.debug("delta is %d for line_len %d (lfragment %s prevsep %s sep %s)",
                        delta, line_len, lfragment, prevsep, sep)

        return lfragment, rfragment


    def pyphen_hypenate(word: str, delta: int) -> Tuple[str, str]:
        # Returns either a 2-tuple or None
        result = pyphen_hyphenator.wrap(word, delta)
        if result:
            lfragment, rfragment = result
            logger.debug("delta is %d for line_len %d (lfragment %s prevsep %s sep %s)",
                         delta, line_len, lfragment, prevsep, sep)
            return lfragment, rfragment
        else:
            logger.debug("'%s' isn't hyphenatable; delta is %d for line_len %d (prevsep %s sep %s)",
                         word, delta, line_len, prevsep, sep)
            raise ValueError("Unhyphenatable word '%s'" % word, word)


    # -- create_folded_para() --
    hypenate_fn = {'simple': simple_hypenate, 'pyphen': pyphen_hypenate, 'none': None}[justifier.params.get('hyphenation', 'pyphen')]
    line_width = justifier.params.get('line_width', 60)
    min_fragment_len = min(3, line_width / 20)
    line_chunks = []  # List[Chunk]
    try:
        line_len = 0   # Length not including separator part of final Chunk
        prevsep = ""
        # Build a line out of chunk-tuples then render it to a string
        while True:
            # Pull enough words to completely fill a line
            while True:
                word, sep = yield
                if line_len + len(prevsep) + len(word) <= line_width:
                    line_chunks.append(Chunk(word, sep))
                    line_len += len(prevsep) + len(word)
                    prevsep = sep
                else:
                    break

            # delta is number of spaces to be added to the line
            delta = line_width - line_len
            # (Try to) split the word
            if hypenate_fn and delta-len(prevsep) >= min_fragment_len and \
                    len(word) >= min_fragment_len * 2:
                try:
                    # If we add a fragment to this line, separator won't be at
                    # the end any more and so will count against the delta
                    lfragment, rfragment = hypenate_fn(word, delta - len(prevsep))

                    # Hyphenation succeeded
                    line_chunks.append(Chunk(lfragment, " "))
                    delta -= len(lfragment) + len(prevsep)
                except ValueError:
                    lfragment = ""
            else:
                logger.debug("not hyphenating; delta is %d for line_len %d of %d words (prevsep %s sep %s)",
                             delta, line_len, len(line_chunks), prevsep, sep)
                lfragment = ""

            if not lfragment:
                # No fragment added to this line; whole word is carried over to
                # the next line and so delta includes width of prevsep
                rfragment = word

            # Seed the next iteration
            prevsep = sep
            line_len = len(rfragment)

            # Pad the partial line
            num_words = len(line_chunks)
            # (Initially, this is done with simple spaces but should use a
            # selection of weighted tweaks instead)
            while delta > 0:
                # First, pick words that end with "." -- count might be > delta
                full_stop_wordnums = [n for n in range(num_words - 1) if line_chunks[n].word.endswith(".")]
                # Then just pick random words
                if num_words > 1 and delta > len(full_stop_wordnums):
                    sample_count = min(num_words - 1, delta - len(full_stop_wordnums))
                    random_wordnums = random.sample(range(num_words - 1), sample_count)
                else:
                    # Slice the array if not all needed
                    if len(full_stop_wordnums) > delta:
                        full_stop_wordnums = full_stop_wordnums[0:delta]

                    random_wordnums = []

                all_wordnums = full_stop_wordnums + random_wordnums
                if all_wordnums:
                    delta -= len(all_wordnums)

                    # Pad chunks with given numbers
                    ## logger.debug("Padding %d for line ending %s", delta, lfragment)
                    for n in all_wordnums:
                        new_chunk = Chunk(line_chunks[n].word, line_chunks[n].sep + " ")
                        line_chunks[n] = new_chunk
                else:
                    # Give up iterating if no padding opportunities were found
                    break

            # Send the finished line
            dest.send(line_render(line_chunks))

            # Text to be prepended to the next line
            if rfragment:
                line_chunks = [Chunk(rfragment, prevsep)]
            else:
                line_chunks = []

    except StopIteration:
        # Ignore yield failure due to running out of words
        pass

    except GeneratorExit:
        pass

    finally:
        # Just print the remaining partial line without doing anything to it
        if line_chunks:
            dest.send(line_render(line_chunks))


def indent_lines(indent: int, dest: Generator):
    prefix = " " * indent

    try:
        while True:
            line = yield
            dest.send(prefix + line)

    except StopIteration:
        # Ignore yield failure due to running out of lines
        pass

    except GeneratorExit:
        pass


def collate_lines(dest: Generator):
    """
    Generator that takes a series of items and collects them into a single
    string separated by newlines, which is sent to dest.

    TO-DO: If None is received, assemble and send the current collection then restart
    """

    try:
        lines = []
        while True:
            line = yield
            lines.append(line)

    except StopIteration:
        # Ignore yield failure due to running out of lines
        pass

    except GeneratorExit:
        pass

    finally:
        # Just print the remaining partial line without doing anything to it
        if lines:
            para = "\n".join(lines)
            dest.send(para)


def print_paras():
    ## logger.debug("print_paras started")
    prev = False
    try:
        while True:
            para = yield
            # Blank line between paragraphs
            if prev:
                print()
            print(para)
            prev = True
    except GeneratorExit:
        pass


## def justify(input: TextIO):
##     """
##     Takes a bunch of lines of input, splits into paragraphs and formats
##     """
## 
##     pg = process_paras()
##     for line in pg.send():
##         print(line)


def init(parent_logger: logging.Logger):
    global p, logger, pyphen_hyphenator

    logger = parent_logger.getChild("justifier")

    if justifier.params.get('hyphenation') == 'pyphen':
        pyphen_hyphenator = pyphen.Pyphen(lang=locale.getlocale()[0])

    # reformat() uses create_folded_para(), possibly indent_lines() and collate_lines() in a sub-pipeline
    p = utils.Pipeline(get_paras, reformat, print_paras)
    ## print(p.chain[0])
    ## p = FixedPipeline()


def process(input: Iterable[str]):
    p.send_lines(input)


def finalise():
    p.close()
