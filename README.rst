=====================
interactive-organizer
=====================
Interactively and manually organize ebook files quickly. This is a Python port of `interactive-organizer.sh <https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh>`_ 
from `ebook-tools <https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

.. contents:: **Contents**
   :depth: 3
   :local:
   :backlinks: top
 
About
=====
Interactively and manually organize ebook files quickly. It is a very interesting script developed originally by `na-- <https://github.com/na-->`_
since you can manually check the files that were automatically renamed by `organized_ebooks <https://github.com/raul23/organize-ebooks>`_
directly in the terminal. Many useful operations can be performed through the terminal for each ebook that you want to check:

- read the file content (text conversion) from the terminal by leveraging the ``less`` command
- read the book's metadata from the corresponding ``.meta`` file
- provide the correct ISBN and the file will be renamed by fetching metadata from online sources
- and so on!

This is a Python port of `interactive-organizer.sh <https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh>`_ 
from `ebook-tools <https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

`:star:` Other related Python projects based on ``ebook-tools``:

- `convert-to-txt <https://github.com/raul23/convert-to-txt>`_: convert documents (pdf, djvu, epub, word) to txt
- `find-isbns <https://github.com/raul23/find-isbns>`_: find ISBNs from ebooks (pdf, djvu, epub) or any string given as input to the script
- `ocr <https://github.com/raul23/ocr>`_: run OCR on documents (pdf, djvu, and images)
- `split-ebooks-into-folders <https://github.com/raul23/split-ebooks-into-folders>`_: split the supplied ebook files into 
  folders with consecutive names
- `organize-ebooks <https://github.com/raul23/organize-ebooks>`_: automatically organize folders with potentially huge amounts of 
  unorganized ebooks. It leverages the first three previous Python scripts.

Dependencies
============

Installing with Docker (Recommended) ⭐
=======================================

Installing the development version
==================================
Install
-------

Uninstall
---------

Script options
==============
List of options
---------------

Explaining some of the options/arguments
----------------------------------------

Script usage
============

Example: manually organize a collection of documents
====================================================
Through the script ``interactive_organizer.py``
-----------------------------------------------

Through the Python API
----------------------
