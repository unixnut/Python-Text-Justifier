"""Main module."""

from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import re
import logging
from collections import namedtuple
import random

import justifier   # This package's top-level module


# *** DEFINITIONS ***
logger: logging.Logger = None
p = None  # Pipeline


# *** CLASSES ***
Chunk = namedtuple('Chunk', ['word', 'sep'])


class Pipeline:
    """
    Automatically build a chain of generators.

    Warning: Generator functions must NOT call `dest.close()` in their
    GeneratorExit catch block or `finally` block.  The chain is closed in order
    by this class's close() method.

    If a generator is garbage-collected prior to the one before it in the chain
    doing the final send, a StopIteration error will be raised; See
    https://docs.python.org/3/reference/expressions.html#generator.send 
    """

    def __init__(self, *args):
        self.chain = []
        prevdest = {}
        # Create and start the generators, in reverse order
        for generator_class in reversed(args):
            logger.debug(repr(generator_class))
            generator = generator_class(**prevdest)
            generator.send(None)
            prevdest = {'dest': generator}
            self.chain.insert(0, generator)


    def process(self, input: Iterable[str]):
        for line in input:
            self.chain[0].send(line.rstrip())


    def close(self):
        """
        Close generators in order so that none are left trying to send() to
        a closed generator (happens during random garbage collection and raises
        a StopIteration error).
        """
        for g in self.chain:
            g.close()


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

    def chunk_to_words(s: str, dest: Generator):
        logger.debug("chunk_to_words started; %s", repr(dest))

        # Do we need to chop the last separator?
        for match in reo.finditer(para):
            if match:
                chunk = (match.group(1), match.group(2) or "")
            else:
                chunk = ("", "")
            g.send(chunk)

    sep_regex = justifier.params.get('sep_regex', r"\s")
    reo = re.compile("((?:(?!%s).)+)((?:%s)*)" % (sep_regex, sep_regex))
    try:
        while True:
            para = yield
            ## logger.debug(para)

            # Mini-pipeline that fans-in to this generator's dest
            # Create and start the generators in reverse order
            coll = collate_lines(dest)
            coll.send(None)
            g = create_folded_para(coll)
            g.send(None)

            # Run the mini-pipeline
            chunk_to_words(para, g)

            # Clean up the mini-pipeline in forwards order
            g.close()
            coll.close()

    except GeneratorExit:
        pass


def create_folded_para(dest: Generator):
    """
    Coroutine that formats a series of words into a paragraph.
    @p dest: Next generator object

    @warning Not a main-chain generator, so do NOT close `dest`.
    """

    def line_render(a: List[Chunk]):
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


    hypenate_fn = simple_hypenate
    right_margin = justifier.params.get('right_margin', 60)
    min_fragment_len = right_margin / 20
    line_chunks: List[Chunk] = []
    try:
        line_len = 0   # Length not including separator part of last Chunk
        prevsep = ""
        # Build a line out of chunk-tuples then render it to a string
        while True:
            # Pull enough words to completely fill a line
            while True:
                word, sep = yield
                if line_len + len(prevsep) + len(word) <= right_margin:
                    line_chunks.append(Chunk(word, sep))
                    line_len += len(prevsep) + len(word)
                    prevsep = sep
                else:
                    break

            # If we add a fragment to this line, padding won't be at the end
            # any more and so won't count as part of the delta
            delta = right_margin - line_len - len(prevsep)
            # (Try to) split the word
            if hypenate_fn and delta > 2 and len(word) >= min_fragment_len * 2:
                lfragment, rfragment = hypenate_fn(word, delta)
                line_chunks.append(Chunk(lfragment, " "))
                delta -= len(lfragment)
            else:
                lfragment = ""
                rfragment = word
                # No fragment added to this line so add the separator back into the delta
                delta += len(prevsep)

            # Seed the next iteration
            prevsep = sep
            line_len = len(rfragment)

            # Pad the line
            # (Initially, this is done with simple spaces but should use a
            # selection of weighted tweaks instead)
            if delta > 0:
                # pad chunks with given numbers
                ## logger.debug("Padding %d for line ending %s", delta, lfragment)
                for n in random.sample(range(len(line_chunks) - 1), delta):
                    new_chunk = Chunk(line_chunks[n].word, line_chunks[n].sep + " ")
                    line_chunks[n] = new_chunk

            dest.send(line_render(line_chunks))

            # Data to be prepended to the next line
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


def collate_lines(dest: Generator):
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
    global p, logger

    logger = parent_logger.getChild("justifier")

    # reformat() uses create_folded_para() and collate_lines() in a sub-pipeline
    p = Pipeline(get_paras, reformat, print_paras)
    ## print(p.chain[0])
    ## p = FixedPipeline()


def process(input: Iterable[str]):
    p.process(input)


def finalise():
    p.close()
