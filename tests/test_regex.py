import unittest
import re

from justifier import justifier


class TestRegex(unittest.TestCase):
    """Tests for Regex functionality."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_regex(self):
        sep_regex = r"\s"
        regex = "((?:(?!%s).)+)((?:%s)*)" % (sep_regex, sep_regex)
        reo = re.compile(regex)
        match = reo.match("Snozz  ")
        if match:
            chunk = match.group(1) + ";" + match.group(2) + "^"
        else:
            chunk = "<>"
        self.assertEqual("Snozz;  ^", chunk)

