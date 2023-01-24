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

Personally, this is the shell script from ``na--`` that I had the most fun porting* to Python since it shows the powerful and interesting
things you can do through the terminal and all via a Python script: you can even invoke a bash shell directly from the python script and then go 
back to the Python script as if nothing happened! 

What I also like is how ``na--`` had the great idea of highlighting the differences in the old
filename compared to the new one for a given renamed ebook. Similar words between both filenames are colored green and those missing
in the new filename are colored red. Hence you can quickly see if the file was renamed correctly.

\* all ``na--`` shell scripts were a lot of fun to port but this one really is special since you interact more with it than the others

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
`:warning:` 

   You can ignore this section and go straight to pulling the `Docker image <#installing-with-docker-recommended>`_ which contains all the 
   required dependencies and the Python package ``interactive_organizer`` already installed. This section is more for showing how I setup my system
   when porting the shell script `interactive-organizer.sh <https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh>`_ et al. 
   to Python.

This is the environment on which the Python package `interactive_organizer <./interactive_organizer/>`_ was developed and tested:

* **Platform:** macOS
* **Python**: version **3.7**
* `textutil <https://ss64.com/osx/textutil.html>`_ or `catdoc <http://www.wagner.pp.ru/~vitus/software/catdoc/>`_: for converting *doc* to *txt*

  **NOTE:** On macOS, you don't need ``catdoc`` since it has the built-in ``textutil``
  command-line tool that converts any *txt*, *html*, *rtf*, 
  *rtfd*, *doc*, *docx*, *wordml*, *odt*, or *webarchive* file
* `DjVuLibre <http://djvu.sourceforge.net/>`_: it includes ``djvutxt`` for converting *djvu* to *txt*
  
    `:warning:` 
  
    - To access the *djvu* command line utilities and their documentation, you must set the shell variable ``PATH`` and ``MANPATH`` appropriately. 
      This can be achieved by invoking a convenient shell script hidden inside the application bundle::
  
       $ eval `/Applications/DjView.app/Contents/setpath.sh`
   
      **Ref.:** ReadMe from DjVuLibre
    - You need to softlink ``djvutxt`` in ``/user/local/bin`` (or add it in ``$PATH``)
* `poppler <https://poppler.freedesktop.org/>`_: it includes ``pdftotext`` for converting *pdf* to *txt*

`:information_source:` *epub* is converted to *txt* by using ``unzip -c {input_file}``

|

**Optionally:**

- `calibre <https://calibre-ebook.com/>`_: 

  - Versions **2.84** and above are preferred because of their ability to manually specify from which
    specific online source we want to fetch metadata. For earlier versions you have to set 
    ``ISBN_METADATA_FETCH_ORDER`` and ``ORGANIZE_WITHOUT_ISBN_SOURCES`` to empty strings.

  - for fetching metadata from online sources
  
  - for getting an ebook's metadata with ``ebook-meta`` in order to search it for ISBNs

  - for converting {*pdf*, *djvu*, *epub*, *msword*} to *txt* (for ISBN searching) by using calibre's 
    `ebook-convert <https://manual.calibre-ebook.com/generated/en/ebook-convert.html>`_
  
    `:warning:` ``ebook-convert`` is slower than the other conversion tools (``textutil``, ``catdoc``, ``pdftotext``, ``djvutxt``)

- **Optionally** `poppler <https://poppler.freedesktop.org/>`_, `catdoc <http://www.wagner.pp.ru/~vitus/software/catdoc/>`_ 
  and `DjVuLibre <http://djvu.sourceforge.net/>`_ can be installed for **faster** than calibre's conversion of ``.pdf``, ``.doc`` and ``.djvu`` files
  respectively to ``.txt``.

- **Optionally** the `Goodreads <https://www.mobileread.com/forums/showthread.php?t=130638>`_ and 
  `WorldCat xISBN <https://github.com/na--/calibre-worldcat-xisbn-metadata-plugin>`_ calibre plugins can be installed for better metadata fetching.

|

`:star:`

  If you only install **calibre** among these dependencies, you can still have
  a functioning program that will enable you to manually organize your ebook collections
  with the script ``interactive_organizer``: 
  
  * fetching metadata from online sources (very helpful feature for this particular script) 
    will work: by `default 
    <https://manual.calibre-ebook.com/generated/en/fetch-ebook-metadata.html#
    cmdoption-fetch-ebook-metadata-allowed-plugin>`__
    **calibre** comes with Amazon and Google sources among others
  * conversion to *txt* will work: `calibre`'s own ``ebook-convert`` tool
    will be used. However, accuracy and performance will be affected as explained 
    in the list of dependencies above.

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
