=====================
interactive-organizer
=====================
Interactively and manually organize ebook files quickly. This is a Python port of `interactive-organizer.sh <https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh>`_ 
from `ebook-tools <https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

.. image:: ./images/basic_command_menu.png
   :target: ./images/basic_command_menu.png
   :align: left
   :alt: Highlight in the old filename showing differences with new filename
 
About
=====
With `interactive_organizer.py 
<https://github.com/raul23/interactive-organizer/blob/main/interactive_organizer/scripts/interactive_organizer.py>`_, 
you can interactively and manually organize ebook files quickly. It allows you to manually check the files that were automatically renamed by 
`organized_ebooks <https://github.com/raul23/organize-ebooks>`_ directly in the terminal. Many useful operations can be 
performed through the terminal for each ebook that you want to check:

- read the file content (text conversion) from the terminal by leveraging the ``less`` command,
- read the book's metadata from the corresponding ``.meta`` file,
- provide another ISBN that will be used to fetch metadata from online sources and use these metadata to rename the file,
- and so on!

This is a Python port of `interactive-organizer.sh <https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh>`_ 
from `ebook-tools <https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.

Personally, this is the shell script from ``na--`` that I had the most fun porting* to Python since it shows the powerful and interesting
things that you can do through the terminal and all via a Python script: you can even invoke a bash shell directly from the Python script, do your 
thing with the bash shell like create a folder over here and a file over there and then go back to the Python script as if nothing happened! 

What I also like is how ``na--`` had the great idea of highlighting the differences in the old
filename compared to the new one for a given renamed ebook. Similar words between both filenames are colored green and those missing
in the new filename are colored red. Hence you can quickly see if the file was renamed correctly.

.. image:: ./images/basic_command_menu.png
   :target: ./images/basic_command_menu.png
   :align: left
   :alt: Highlight in the old filename showing differences with new filename

|

\* all ``na--`` shell scripts were a lot of fun to port but this one really is special for its interactivity 

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
* `organize_ebooks <https://github.com/raul23/organize-ebooks>`_: Python package whose `library 
  <https://github.com/raul23/organize-ebooks/blob/main/organize_ebooks/lib.py>`_ has lots of useful functions
  for developing ebook organizers/managers. It is a Python port of `organize-ebooks.sh 
  <https://github.com/na--/ebook-tools/blob/master/organize-ebooks.sh>`_ 
  from `ebook-tools <https://github.com/na--/ebook-tools>`_ written in shell by `na-- <https://github.com/na-->`_.
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

`:information_source:` *epub* can be converted to *txt* by using ``unzip -c {input_file}``

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
`:information_source:` 

  It is recommended to install the Python package `interactive_organizer <./interactive_organizer/>`_ with **Docker** because the Docker
  container has all the many `dependencies <#dependencies>`_ already installed along with the Python package ``interactive_organizer``. 

1. Pull the Docker image from `hub.docker.com <https://hub.docker.com/repository/docker/raul23/organize/general>`_:

   .. code-block:: bash

      docker pull raul23/organize:latest

2. Run the Docker container:

   .. code-block:: bash

      docker run -it -v /host/input/folder:/books_to_check raul23/organize:latest
   
   `:information_source:` 
   
      - ``/host/input/folder`` is a directory within your OS that can contain all the ebooks to be manually organized and
        is mounted as ``/books_to_check`` within the Docker container.
      - You can use the ``-v`` option mulitple times to mount several host output folders within the container, e.g.:
        
        .. code-block:: bash
        
           docker run -it -v /host/input/folder:/books_to_check -v /host/output/folder:/output-folder raul23/organize:latest
      - ``raul23/organize:latest`` is the name of the image upon which the Docker container will be created.

3. Now that you are within the Docker container, you can run the Python script ``interactive_organizer`` with 
   the desired `options <#script-s-list-of-options>`_::

    user:~$ interactive_organizer /books_to_check/
   
   `:information_source:` 
   
       - This basic command instructs the script ``interactive_organizer`` to start manually checking the ebooks within ``/books_to_check/``.
       - When you log in as ``user`` (non-root) within the Docker container, your working directory is ``/ebook-tools``.

`:information_source:` The Docker image also comes with the Python package `organize_ebooks <https://github.com/raul23/organize-ebooks>`_. You
can find more information about the content of the Docker image at `github.com/raul23/organize-ebook 
<https://github.com/raul23/organize-ebooks#content-of-the-docker-image>`_

Installing the development version
==================================
Install
-------
`:warning:` 

   You can ignore this section and go straight to pulling the `Docker image <#installing-with-docker-recommended>`_ which contains all the 
   required dependencies and the Python package ``interactive_organizer`` already installed. This section is for installing the bleeding-edge
   version of the Python package ``interactive_organizer`` after you have installed yourself the many `dependencies <#dependencies>`_.
  
After you have installed the `dependencies <#dependencies>`_, you can then install the development (bleeding-edge) 
version of the package `interactive_organizer <./interactive_organizer/>`_:

.. code-block:: bash
 
   pip install git+https://github.com/raul23/interactive-organizer#egg=interactive-organizer
 
**NOTE:** the development version has the latest features 
 
**Test installation**

1. Test your installation by importing ``interactive_organizer`` and printing its
   version:
   
   .. code-block:: bash

      python -c "import interactive_organizer; print(interactive_organizer.__version__)"

2. You can also test that you have access to the ``interactive_organizer.py`` script by
   showing the program's version:

   .. code-block:: bash

      interactive_organizer --version

Uninstall
---------
To uninstall the development version of the package `interactive_organizer <./interactive_organizer/>`_
along with the dependency `organize_ebooks <https://github.com/raul23/organize-ebooks>`_:

.. code-block:: bash

   pip uninstall interactive_organizer organize_ebooks

Script's list of options
========================
To display `organize_ebooks.py <./find_iorganize_ebooks/scripts/organize_ebooks.py>`_'s list of options and their descriptions::

   $ interactive_organizer -h
   usage: interactive_organizer [OPTIONS] {folder_to_organize} -o {output_folder} [{output_folder}]

   Interactively and manually organize ebook files quickly.

   This script is based on the great ebook-tools written in shell by na-- (See https://github.com/na--/ebook-tools).

   General options:
     -h, --help                                    Show this help message and exit.
     -v, --version                                 Show program's version number and exit.
     -q, --quiet                                   Enable quiet mode, i.e. nothing will be printed.
     --verbose                                     Print various debugging information, e.g. print traceback when there is an exception.
     -d, --dry-run                                 If this is enabled, no file rename/move/symlink/etc. operations will actually be executed.
     -s, --symlink-only                            Instead of moving the ebook files, create symbolic links to them.
     --log-level {debug,info,warning,error}        Set logging level. (default: info)
     --log-format {console,only_msg,simple}        Set logging formatter. (default: only_msg)

   Convert-to-txt options:
     --djvu {djvutxt,ebook-convert}                Set the conversion method for djvu documents. (default: djvutxt)
     --epub {epubtxt,ebook-convert}                Set the conversion method for epub documents. (default: ebook-convert)
     --msword {catdoc,textutil,ebook-convert}      Set the conversion method for epub documents. (default: textutil)
     --pdf {pdftotext,ebook-convert}               Set the conversion method for pdf documents. (default: pdftotext)

   Interactive options:
     --qm, --quick-mode                            This mode is useful when `organize_ebooks` was called with `--keep-metadata`. Ebooks that contain 
                                                   all of the tokens from the old file name in the new one are directly moved to the default output 
                                                   folder.
     --token-min-length LENGTH                     When files and file metadata are parsed, they are split into words and ones shorter than this value 
                                                   are ignored. By default, single and two character number and words are ignored. (default: 3)
     --tokens-to-ignore TOKENS                     A regular expression that is matched against the filename/author/title tokens and matching tokens 
                                                   are ignored. The default regular expression includes common words that probably hinder online 
                                                   metadata searching like book, novel, series, volume and others, as well as probable publication 
                                                   years like (so 1999 is ignored while 2033 is not).
                                                   (default: ebook|book|novel|series|^ed(ition)?$|^vol(ume)?$|(19[0-9]|20[0-2])[0-9])
     -m, ---metadata-fetch-order METADATA_SOURCE [METADATA_SOURCE ...]
                                                   This option allows you to specify the online metadata sources and order in 
                                                   which the subcommands will try searching in them for books by their ISBN. 
                                                   The actual search is done by calibre's `fetch-ebook-metadata` 
                                                   command-line application, so any custom calibre metadata plugins can also 
                                                   be used. To see the currently available options, run 
                                                   `fetch-ebook-metadata --help` and check the description for the 
                                                   `--allowed-plugin` option. If you use Calibre versions that are older than 
                                                   2.84, it's required to manually set this option to an empty string.
                                                   (default: ['Goodreads', 'Google', 'Amazon.com', 'ISBNDB', 'WorldCat xISBN', 
                                                   'OZON.ru'])
     --owis, --organize-without-isbn-sources METADATA_SOURCE [METADATA_SOURCE ...]
                                                   This option allows you to specify the online metadata sources in which the 
                                                   script will try searching for books by non-ISBN metadata (i.e. author and 
                                                   title). The actual search is done by calibre's `fetch-ebook-metadata`
                                                   command-line application, so any custom calibre metadata plugins can also 
                                                   be used. To see the currently available options, run 
                                                   `fetch-ebook-metadata --help` and check the description for the 
                                                   `--allowed-plugin` option. Because Calibre versions older than 2.84 don't 
                                                   support the `--allowed-plugin` option, if you want to use such an old
                                                   Calibre version you should manually set `organize_without_isbn_sources` to 
                                                   an empty string. (default: ['Goodreads', 'Google','Amazon.com'])

   Input/Output options:
     folder_to_organize                            Folder containing the ebook files that need to be organized.
     -o, --output-folders [PATH [PATH ...]]        The different output folders to which you can quickly move ebook files. The first specified folder 
                                                   is the default.
     -c, --custom-move-base-dir PATH               A base directory in whose sub-folders files can more easily be moved during the interactive session 
                                                   because of tab autocompletion. (default: )
     -r, --restore-original-base-dir PATH          If you want to enable the option of restoring files to their original folders (or at least with the 
                                                   same folder structure), set this as the base path. (default: )
     --oft, --output-filename-template TEMPLATE    This specifies how the filenames of the organized files will look. It is a 
                                                   bash string that is evaluated so it can be very flexible (and also 
                                                   potentially unsafe). (default: ${d[AUTHORS]// & /, } - ${d[SERIES]:+
                                                   [${d[SERIES]}] - }${d[TITLE]/:/ -}${d[PUBLISHED]:+ 
                                                   (${d[PUBLISHED]%-*})}${d[ISBN]:+[${d[ISBN]}]}.${d[EXT]})
     --ome, --output-metadata-extension EXTENSION  This is the extension of the additional metadata file
                                                   that is saved next to each newly renamed file.
                                                   (default: meta)

Script usage
============
Menu options
------------
Let's say that we want to manually organize some books that were labeled as uncertain by the script 
`organize_ebooks <https://github.com/raul23/organize-ebooks>`_ that automatically organized a 
collection of ebooks. Here is a basic command that will allow you to manually inspect these uncertain
books::

   $ interactive_organizer ~/test/test_organize/commons-books/uncertain/

.. image:: ./images/basic_command_menu.png
   :target: ./images/basic_command_menu.png
   :align: left
   :alt: Basic command: main menu

We will go through each of the options in the main menu using this simple command as a starter.

`:information_source:` 

   Ebooks that the script ``organize_ebooks`` was able to identify from non-ISBN metadata (e.g. title)
   fetched from online sources (e.g. Goodreads) are saved in a folder specified by the option `output-folder-uncertain 
   <https://github.com/raul23/organize-ebooks#list-of-options>`_. An ebook considered as "uncertain" means that the 
   script is not highly confident about the filenames given to these books compared to those books whose ISBNs 
   could be retrieved directly from their contents and successfully used to retrieve metadata from online sources.

`:star:`

  When you are in a submenu (e.g. moving file with the `m <#m-move-to-another-folder>`_ option) and want to go back 
  to the main menu, you can do it by pressing the keys ``Ctrl`` and ``C``.

No metadata file found
""""""""""""""""""""""
The user will be warned if an ebook file doesn't have an associated metadata file (as created by the script 
`organize_ebooks <https://github.com/raul23/organize-ebooks#explaining-some-of-the-options-arguments>`_):

.. image:: ./images/no_metadata2.png
   :target: ./images/no_metadata2.png
   :align: left
   :alt: User warned because no metadata file was found

|

You can still do all of the operations in the main menu except the `c <#read-the-saved-metadata-file>`_ option obviously: 

.. image:: ./images/no_metadata_c_option_fails.png
   :target: ./images/no_metadata_c_option_fails.png
   :align: left
   :alt: 'c' option fails because no metadata

``M``: move to another folder
"""""""""""""""""""""""""""""
Press the key ``M`` to move the current ebook file to another folder:

.. image:: ./images/move_file2.png
   :target: ./images/move_file2.png
   :align: left
   :alt: Entering the new path where the file will be moved

`:warning:` As noted by the script, the metadata file will be deleted if it is to be found.

The script warns you that the 'custom' folder is empty because the `basic command <#basic-command>`_ that was used to run 
the ``interactive_organizer`` script didn't use the option ``custom-move-base-dir`` (by default it is set to empty). Thus, 
the new path starts from the current working directory. 

The file in this example will be saved relative to the current working directory but you can also give a full path.

|

By using tab, the script autocompletes the path that you enter so that it is easier for you to navigate through your filesystem:

.. image:: ./images/move_file_autocompletes.png
   :target: ./images/move_file_autocompletes.png
   :align: left
   :alt: Autocompleting your new path

``O/Enter``: open file in external viewer 
"""""""""""""""""""""""""""""""""""""""""
Pressing the key ``O`` or ``Enter`` will open the given document in an external program which is the default one used
by the OS for this particular file type. On Linux, this default program is called upon by ``xdg-open`` and on macOS, it is done
by ``open``.

Thus you can check the content of the PDF to make sure that the file was correctly renamed. 

.. image:: ./images/open_viewer_program_menu.png
   :target: ./images/open_viewer_program_menu.png
   :align: left
   :alt: External program option chosen from main menu
   
.. image:: ./images/viewer_program_ibooks.png
   :target: ./images/viewer_program_ibooks.png
   :align: left
   :alt: External program: iBooks

``C``: read the saved metadata file
"""""""""""""""""""""""""""""""""""
For each ebook that the script `organize_ebooks <https://github.com/raul23/organize-ebooks#explaining-some-of-the-options-arguments>`_ 
(``keep-metadata`` option) renames and moves to another folder, a metadata file is created with data fetched from online 
sources via calibre's ``fetch-ebook-metadata``.

This metadata file can be read from within the Python script by pressing the key ``C`` from the main menu:

.. image:: ./images/read_saved_metadata_file.png
   :target: ./images/read_saved_metadata_file.png
   :align: left
   :alt: Reading the saved metadata file
   
``T/```: run shell in terminal
"""""""""""""""""""""""""""""""
To open a shell from within the Python script, press the key ``T`` or ````` (backtick):

.. image:: ./images/shell.png
   :target: ./images/shell.png
   :align: left
   :alt: Run shell in terminal via Python script

|

To exit from the shell, press the keys ``Ctrl`` and ``D`` and you will get back to the main menu of the Python script:

.. image:: ./images/shell_exit2.png
   :target: ./images/shell_exit2.png
   :align: left
   :alt: Exit shell

``S``: skip file
""""""""""""""""
You can skip the current ebook file by pressing the key ``S``. If another file is found in the input folder, it
will be shown in the main menu as the next file to be checked by the user:

.. image:: ./images/skip_file.png
   :target: ./images/skip_file.png
   :align: left
   :alt: Skip file

``I/Backspace``: interactively reorganize the file
""""""""""""""""""""""""""""""""""""""""""""""""""
This is the part of the menu where you will interact a lot with the script. When pressing the key ``I`` or ``Backspace``,
you are asked to enter search terms or a new filename within single quotes:

.. image:: ./images/interactive_enter.png
   :target: ./images/interactive_enter.png
   :align: left
   :alt: 'i' option: enter search terms or a new filename

`:information_source:` The old file path will be added into the new metadata file since the old metadata file is removed.

The search terms will be used to fetch new metadata from online sources via calibre's ``fetch-ebook-metadata``. These fetched
metadata will be used to rename the given ebook file. The file will be saved within the same input folder.

`:warning:` The script distinguishes search terms and the new filename by considering anything within single quotes
as the new filename.

.. image:: ./images/interactive_single_quotes.png
   :target: ./images/interactive_single_quotes.png
   :align: left
   :alt: New filename within single quotes

|

You could also enter a new ISBN as the search term and it will be used to rename the file:

.. image:: ./images/interactive_new_isbn.png
   :target: ./images/interactive_new_isbn.png
   :align: left
   :alt: ISBN as search term

The script then fetches metadata based on the provided ISBN and displays the metadata that it found:

.. image:: ./images/interactive_metadata.png
   :target: ./images/interactive_metadata.png
   :align: left
   :alt: Fetch metadata based on provided ISBN

It then asks if you want to use these metadata to rename the ebook file and the associated metadata file:

.. image:: ./images/interactive_rename.png
   :target: ./images/interactive_rename.png
   :align: left
   :alt: Use fetched metadata to rename file

``L``: read in terminal (with ``less``)
"""""""""""""""""""""""""""""""""""""""
To read the given document from the terminal, press the key ``L`` which will instruct the script to convert
the file (e.g. pdf, djvu, epub) to text and show the content in the terminal through the program ``less``.

``less`` will let you move easily through the content (page up and page down) and hence you can quickly take
a peek at the content of the file to check if it was correctly named by the automatic script ``organize_ebooks``.

Here is the text content of the epub document from the example as shown by ``less``:

.. image:: ./images/less_epub2.png
   :target: ./images/less_epub2.png
   :align: left
   :alt: Text content from EPUB with less

|

And here is a sample text content from a PDF file when viewing it with ``less``:

.. image:: ./images/less_pdf.png
   :target: ./images/less_pdf.png
   :align: left
   :alt: Text content from PDF with less

|

`:information_source:` You can then press ``Q`` to exit from ``less`` and get back to the main menu of the Python script.

``?``: run ebook-meta on the file
"""""""""""""""""""""""""""""""""
Press ``?`` to show the metadata of the given document via calibre's ``ebook-meta``:

.. image:: ./images/ebook_meta.png
   :target: ./images/ebook_meta.png
   :align: left
   :alt: Show book metadata with ebook-meta

``E``: eval code (change env vars)
""""""""""""""""""""""""""""""""""
Press the key ``E`` to modify the regex used for ignoring tokens in the old filename when comparing the old
and new filenames:

.. image:: ./images/eval.png
   :target: ./images/eval.png
   :align: left
   :alt: Eval regex for ignoring tokens in filename

Command-line options
--------------------
Quick mode: ``--qm, --quick-mode``
""""""""""""""""""""""""""""""""""
If the new filename for a given ebook file is not missing word from the old filename, the ebook
file can be quickly moved to a user specified folder by using the flag ``--qm`` which enables quick mode:

.. code-block:: bash

   interactive_organizer ~/test/test_organize/commons-books/uncertain/ -o output1/ --qm

`:warning:` It is important to specify at least an output folder with the option ``-o`` since it is the first 
of the output folders that will be used as the location where the ebook file will be saved.

.. image:: ./images/quick_mode_file_moved2.png
   :target: ./images/quick_mode_file_moved2.png
   :align: left
   :alt: Quick mode moves file to output folder

Output folders: ``-o, --output-folders``
""""""""""""""""""""""""""""""""""""""""
We can provide a list of output folders that we can use to move ebook and metadata files between them with the command-line 
option `-o <#script-s-list-of-options>`_:

.. code-block:: bash

   interactive_organizer ~/test/test_organize/commons-books/uncertain/ -o output0 output1 output2/ output3/

.. image:: ./images/output_folders_menu3.png
   :target: ./images/output_folders_menu3.png
   :align: left
   :alt: Output folders in the menu

In the main menu, we can see at the beginning of possible actions four options related to the output folders. 
The first output folder specified in the option ``-o`` is the default one and given the number 0 as label. The other
output folders in the example command line are labeled with 1, 2 and 3.

If we type ``0``, the given ebook file along with the associated metadata file are moved to the ``output0/`` folder:

.. image:: ./images/output_folders_default_folder.png
   :target: ./images/output_folders_default_folder.png
   :align: left
   :alt: Moving file and metadata to output0/

Custom base directory: ``-c, --custom-move-base-dir``
"""""""""""""""""""""""""""""""""""""""""""""""""""""
When using the menu option `m <#m-move-to-another-folder>`_, we can provide a custom base folder to the script via 
the ``-c`` command line option:

.. code-block:: bash

   interactive_organizer ~/test/test_organize/commons-books/uncertain/ -c custom/
 
.. image:: ./images/custom_menu.png
   :target: ./images/custom_menu.png
   :align: left
   :alt: Menu: custom folder path

|

The script asks to enter the file path where the ebook file will be moved. We can see that this
file path starts from the custom base folder we provided to the script (``custom/``).

.. image:: ./images/custom_file_path1.png
   :target: ./images/custom_file_path1.png
   :align: left
   :alt: Provide file path

`:warning:` As the script warns, the corresponding metadata file will be removed.

|

We can check that the file was moved to the custom base directory by calling a bash shell
from the Python script (see the menu option `t <#t-run-shell-in-terminal>`_):

.. image:: ./images/custom_file_path2.png
   :target: ./images/custom_file_path2.png
   :align: left
   :alt: Check file was moved

Restore files: ``-r, --restore-original-base-dir`` 
""""""""""""""""""""""""""""""""""""""""""""""""""
We can restore a given ebook file to the original path (or at least the same folder structure) by providing a base path with
the command-line `-r <#script-s-list-of-options>`_:

.. code-block:: bash

   interactive_organizer ~/test/test_organize/commons-books/uncertain/ -r restore/

.. image:: ./images/restore_menu.png
   :target: ./images/restore_menu.png
   :align: left
   :alt: Menu: Restore file option

|

The script then asks if we want to modify the file path that will be used for saving the restored ebook file:

.. image:: ./images/restore_ask.png
   :target: ./images/restore_ask.png
   :align: left
   :alt: Menu: Restore file option

`:warning:` The associated metadata file will be deleted if it exists.

In this example, the file will be restored to the original folder structure by saving it relative to the specifed base path (``restore/``).

|

By using tab, the script autocompletes the path that we enter so that it is easier to navigate through the filesystem:

.. image:: ./images/restore_autocomplete.png
   :target: ./images/restore_autocomplete.png
   :align: left
   :alt: Restore: tab autocomplete

Example: interactively organize a collection of documents
=========================================================
To interactively organize your ebooks, you can start with the following basic command:

.. code-block:: bash
 
   interactive_organizer ~/uncertain/
 
The only required parameter is the input folder that you want to manually check. This input
folder can be for instance the folder containing uncertain ebooks as renamed by the script 
`organize_ebooks <https://github.com/raul23/organize-ebooks>`_.

These ebooks and their associated metadata files can be checked to validate the book's filenames. In the main
menu and for a given ebook file analyzed, you will see the old filename colored as such:

- red for those words missing in the new filename
- green for those words also found in the new filename
- blue for the date

.. image:: ./images/basic_command_menu.png
   :target: ./images/basic_command_menu.png
   :align: left
   :alt: Highlight in the old filename showing differences with new filename

Hence, you can quickly inspect how good of a job the script ``organize_ebooks`` did with the
renaming of an ebook: if there are many green words and very few or no red words, then you can
`move the file <#m-move-to-another-folder>`_ to another folder of your choice.

If no missing words were detected, the file can be `quickly moved <#quick-mode-qm-quick-mode>`_ to an output folder if the 
flag ``--qm`` (quick mode enabled) was used.
