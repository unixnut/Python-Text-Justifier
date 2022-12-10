=====================
Python Text Justifier
=====================


.. image:: https://img.shields.io/pypi/v/justifier.svg
        :target: https://pypi.python.org/pypi/text-justifier

.. image:: https://readthedocs.org/projects/text-justifier/badge/?version=latest
        :target: https://text-justifier.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Justify and hyphenate text in files and/or standard input


* Free software: GNU General Public License v3
* Documentation: https://text-justifier.readthedocs.io.


Features
--------

* TODO

Algorithm
---------
Consider full stop count when deciding to hyphenate?
1. Grab a line's worth of text plus the word that would push it over the limit
1. Count the number of characters in the "safe" line
1. The delta equals the difference between the line length and (limit subtract
   the number of full stops except one at the end of a line)
1. Determine the hyphenation threshold n = limit / 20, i.e. one extra space per
   20 characters
1. If the overflow word is at least n*2 characters long, attempt to hyphenate it
1. Find the largest usable fragment of the overflow word no longer than delta - 1
1. Add the fragment if hyphenating and change delta to (delta subtract (fragment
   length + 1))
1. Add a space after at most (limit subtract line length) full stops (determined randomly)
1. Add a space before and after at most delta/2 full stops and recalculate
   delta
1. Add a space after delta random spaces
1. If hyphenating and the next line's 

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
