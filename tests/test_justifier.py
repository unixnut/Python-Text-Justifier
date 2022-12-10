#!/usr/bin/env python

"""Tests for `justifier` package."""


import unittest
from click.testing import CliRunner

from justifier import justifier
from justifier import cli

text_lines = """Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 

commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint 
occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
mollit anim id est laborum."""


class TestJustifier(unittest.TestCase):
    """Tests for `justifier` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_pargraph_chunking(self):
        """Ensure that paragraphs are identified correctly."""

        results = []

        def record_results():
            try:
                while True:
                    results.append((yield))
                    ## print("Appending")
            except GeneratorExit:
                pass

        # Initialise coroutines
        rr_dest = record_results()
        rr_dest.send(None)
        gp = justifier.get_paras(dest=rr_dest)
        gp.send(None)

        for line in text_lines.split("\n"):
            gp.send(line)
            ## print("Line")
        gp.close()
        result1 = results[0]
        self.assertTrue(result1.startswith("Lorem ipsum dolor sit amet,"), msg="Bad result1: "+result1)
        result2 = results[1]
        self.assertTrue(result2.startswith("commodo consequat."), msg="Bad result2: "+result2)


    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        ## assert result.exit_code == 0
        ## assert 'justifier.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
