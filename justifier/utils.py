from typing import Set, Dict, Sequence, Tuple, List, Union, AnyStr, Iterable, Callable, Generator, Type, Optional, TextIO, IO
import logging

## import justifier   # This package's top-level module


# *** DEFINITIONS ***
logger = None   # logging.Logger


# *** CLASSES ***
class Pipeline:
    """
    Automatically build a chain of generators or equivalent.

    Warning: Generator functions must NOT call `dest.close()` in their
    GeneratorExit catch block or `finally` block.  The chain is closed in order
    by this class's close() method.

    If a generator is garbage-collected prior to the one before it in the chain
    doing the final send, a StopIteration error will be raised; See
    https://docs.python.org/3/reference/expressions.html#generator.send
    """

    def __init__(self, *args):
        """
        Supports the following entities from which to build the chain:
          - generator function
          - class with send() method
          - tuple containing either of the above and a dict of keyword args
          - pre-created generator object (last entity only)

        Each entity must have a close() method.
        All entities but the last must accept a `dest` keyword arg.
        """

        self.chain = []
        prevdest = {}
        # Create and start the generators, in reverse order
        for entity in reversed(args):
            logger.debug(repr(entity))
            if isinstance(entity, Generator):
                # An already-created generator is only supported in last place
                # in the chain, because this is the only place a `dest` arg
                # isn't used
                if not prevdest:
                    generator = entity
                else:
                    raise ValueError("Generator object only supported as last arg")
            elif isinstance(entity, Tuple):
                # Supports a tuple of the form (generator_fn_or_class, {'arg1': 'value', ...})
                prevdest.update(entity[1])
                generator = entity[0](**prevdest)
                if isinstance(generator, Generator):
                    generator.send(None)
            else:
                # Default is to assume that it's a class or a generator
                # function with no extra args
                generator = entity(**prevdest)
                if isinstance(generator, Generator):
                    generator.send(None)

            self.chain.insert(0, generator)

            # Prepare for the next cycle
            prevdest = {'dest': generator}


    def send(self, item):
        """
        Send an item to the first generator.
        """

        self.chain[0].send(item)


    def send_all(self, input: Iterable):
        """
        Send all items from an iterator etc. to the first generator.
        """

        for item in input:
            self.chain[0].send(item)


    def send_lines(self, input: Iterable[str]):
        """
        Convenience function for sending lines read from a file, without their
        line endings, to the first generator.
        """

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
def init(parent_logger: logging.Logger):
    global logger

    logger = parent_logger.getChild("utils")
