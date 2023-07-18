=====================
Python Text Justifier
=====================


.. image:: https://img.shields.io/pypi/v/justifier.svg
        :target: https://pypi.python.org/pypi/text-justifier

.. image:: https://readthedocs.org/projects/text-justifier/badge/?version=latest
        :target: https://text-justifier.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Justify and hyphenate text in files and/or standard input.  The program can be
invoked as either **text-justifier** or **justify** .

Installation/Upgrade
--------------------
**``pip3 install -U text-justifier``**

Options
-------
``-w``, ``--width *INTEGER*``
  Width of text, not counting indent

``-i``, ``--indent *INTEGER*``
  Number of spaces to add before text

``-r``, ``--right-margin *INTEGER*``
  Determine the width of text to suit a specific column, i.e. right margin is
  indent plus width.

``-c``, ``--centre``, ``--no-centre``, ``--center``, ``--no-center``
  Automatically determine line width based on terminal width, with indent
  mirrored on the right.  Will probably not work with indent of 0 (the
  default).  Uses ``$COLUMNS`` if the terminal size cannot be queried.

``-s``, ``--simple-hyphen``
  Use simple hyphenation method.

``-h``, ``--hyphen``
  Use *pyphen* library to hyphenate, which uses OpenOffice hyphenation
  dictionaries.

``-H``, ``--no-hyphenate``
  Turn hyphenation off.


* Free software: GNU General Public License v3
* Documentation: https://text-justifier.readthedocs.io. (TBA)


Features
--------

* Can centre text according to the screen/terminal width
* Indent text

TO DO
-----

* Em dashes (— or --) should be used padded before random padding is done

* Don't hyphenate URLs

* Extract URLs, replace with placeholders and dump after paragraph;
  Use Markdown style or something similar i.e.

   - ``[text](url)`` -> ``[text][URL_PLACEHOLDER]`` and ``[URL_PLACEHOLDER]: url``
   - ``[url] -> [0]`` and ``[0]: url``

* Option (-f *n*) to add a first-line indent to each paragraph

* Option (-n) to split paragraphs on newline instead of blank lines

* Treat lines that begin with a list character as their own paragraph

Algorithm
---------

1.  Grab a line's worth of text plus the word that would push it over the limit
2.  Count the number of characters in the "safe" line
3.  The delta equals the difference between the line length and (limit subtract
    the number of full stops except one at the end of a line)
4.  Determine the hyphenation threshold n = limit / 20, i.e. one extra space per
    20 characters
5.  If the overflow word is at least n*2 characters long, attempt to hyphenate it
6.  Find the largest usable fragment of the overflow word no longer than delta - 1
7.  Add the fragment if hyphenating and change delta to (delta subtract (fragment
    length + 1))
8.  Add a space after at most (limit subtract line length) full stops (determined randomly)
9.  Add a space before and after at most delta/2 em dashes and recalculate delta
10. Add a space after delta random spaces
11. If hyphenating and the next line's delta would be greater than this one's
    without hyphenation, don't hyphenate

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
