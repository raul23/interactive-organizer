"""Interactively and manually organize ebook files quickly.

This is a Python port of `interactive-organizer.sh` from `ebook-tools` written in
shell by `na--`.

Ref.: https://github.com/na--/ebook-tools
"""
import glob
import logging
import os
import platform
import readline
import sys
import termios
import tty
from pathlib import Path
from textwrap import wrap
from unicodedata import combining, normalize

from organize_ebooks.lib import *
# TODO
from interactive_organizer import __version__
# __version__ = '0.1.0'

# import ipdb

logger = logging.getLogger('interactive_lib')
logger.setLevel(logging.CRITICAL + 1)

LATIN = "ä  æ  ǽ  đ ð ƒ ħ ı ł ø ǿ ö  œ  ß  ŧ ü "
ASCII = "ae ae ae d d f h i l o o oe oe ss t ue"

# =====================
# Default config values
# =====================

# Misc options
# ============
DRY_RUN = False
SYMLINK_ONLY = False

# Logging options
# ===============
LOGGING_FORMATTER = 'only_msg'
LOGGING_LEVEL = 'info'

# Convert-to-txt options
# ======================
DJVU_CONVERT_METHOD = 'djvutxt'
EPUB_CONVERT_METHOD = 'ebook-convert'
MSWORD_CONVERT_METHOD = 'textutil'
PDF_CONVERT_METHOD = 'pdftotext'

# Interactive options
# ===================
QUICK_MODE = False
CUSTOM_MOVE_BASE_DIR = ''
RESTORE_ORIGINAL_BASE_DIR = ''
# DIACRITIC_DIFFERENCE_MASKINGS = None
# MATCH_PARTIAL_WORDS = False

# Options related to extracting and searching for non-ISBN metadata
# =================================================================
TOKEN_MIN_LENGTH = 3
# NOTE: Structured -> Structur (ed removed because 'ed(ition)?')
# Thus, '^' before and '$' after 'ed(ition)'. ed not counted as ed(ition) in Structured
TOKENS_TO_IGNORE = f'ebook|book|novel|series|^ed(ition)?$|^vol(ume)?$|{get_re_year()}'


# Ref.: https://stackoverflow.com/a/510404
def getch():
    """Gets a single character from standard input. Does not echo to the screen."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def less(file_path):
    subprocess.call([f'less "{file_path}" </dev/tty >/dev/tty'], shell=True)
    return 0


def open_document(file_path):
    # Command to open the config file with the default application in the
    # OS or the user-specified app, e.g. `open filepath` in macOS opens the
    # file with the default app (e.g. atom)
    cmd_dict = {'Darwin': f'open "{file_path}"',
                'Linux': f'xdg-open "{file_path}"',
                'Windows': f'cmd /c start "" "{file_path}"'}
    # NOTE: check https://bit.ly/31htaOT (pymotw) for output from
    # platform.system on three OSes
    cmd = cmd_dict.get(platform.system())
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def open_with_less(file_path, isbn_direct_files=ISBN_DIRECT_FILES,
                   djvu_convert_method=DJVU_CONVERT_METHOD,
                   epub_convert_method=EPUB_CONVERT_METHOD,
                   msword_convert_method=MSWORD_CONVERT_METHOD,
                   pdf_convert_method=PDF_CONVERT_METHOD, **kwargs):
    func_params = locals().copy()
    func_params.pop('file_path')
    mime_type = get_mime_type(file_path)
    logger.info(f"Reading '{file_path}' ({mime_type}) with less...")
    if mime_type and re.match(isbn_direct_files, mime_type):
        result = less(file_path)
        # logger.info(result.stdout)
        return 0
    tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
    logger.debug(f"Converting ebook to text format...")
    logger.debug(f"Temp file: {tmp_file_txt}")
    result = convert_to_txt(file_path, tmp_file_txt, mime_type, **func_params)
    if result.returncode == 0:
        logger.debug('Conversion to text was successful')
        # TODO: check returncode or stderr
        result = less(tmp_file_txt)
        # logger.info(result.stdout)
    else:
        logger.error(red('There was an error converting the ebook to txt format:'))
        logger.error(red(result.stderr))
    logger.debug(f"Removing tmp file '{tmp_file_txt}'...")
    remove_file(tmp_file_txt)
    return 0


# Ref.:
def path_completer(text, state):
    """
    This is the tab completer for systems paths.
    Only tested on *nix systems
    """
    if '~' in text:
        text = os.path.expanduser(text)
    return [x for x in glob.glob(text+'*')][state]


# Ref.: https://stackoverflow.com/a/71408065
def remove_diacritics(s, outliers=str.maketrans(dict(zip(LATIN.split(), ASCII.split())))):
    return "".join(c for c in normalize("NFD", s.lower().translate(outliers)) if not combining(c))


# Ref.:
def rlinput(prompt, prefill=''):
    readline.set_completer_delims('\t')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(path_completer)
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


class InteractiveOrganizer:
    def __init__(self):
        self.dry_run = DRY_RUN
        self.symlink_only = SYMLINK_ONLY
        # ======================
        # Convert-to-txt options
        # ======================
        self.djvu_convert_method = DJVU_CONVERT_METHOD
        self.epub_convert_method = EPUB_CONVERT_METHOD
        self.msword_convert_method = MSWORD_CONVERT_METHOD
        self.pdf_convert_method = PDF_CONVERT_METHOD
        # ===================
        # Interactive options
        # ===================
        self.quick_mode = QUICK_MODE
        self.token_min_length = TOKEN_MIN_LENGTH
        self.tokens_to_ignore = TOKENS_TO_IGNORE
        # self.diacritic_difference_maskings = DIACRITIC_DIFFERENCE_MASKINGS
        # self.match_partial_words = MATCH_PARTIAL_WORDS
        # ====================
        # Input/Output options
        # ====================
        self.folder_to_organize = None
        self.output_folders = []
        self.custom_move_base_dir = CUSTOM_MOVE_BASE_DIR
        self.restore_original_base_dir = RESTORE_ORIGINAL_BASE_DIR
        self.output_metadata_extension = OUTPUT_METADATA_EXTENSION

    @staticmethod
    def _color_tokens_in_string(s, tokens, color='red'):
        def color_sub(sub):
            if color == 'red':
                return f'REDCODE{sub}NCCODE'
            elif color == 'green':
                return f'GREENCODE{sub}NCCODE'
            elif color == 'blue':
                return f'BLUECODE({sub}NCCODE'
            else:
                return f'YELLOWCODE{sub}NCCODE'
        for token in tokens:
            # NOTE: doesn't work, e.g. for (1st) Oxford (2nd) -> red(Ox)green(for)d [we want Oxford all red]
            # s = s.replace(token, color_token())
            s = re.sub(r"([\W\d_]*)({})([\W\d_]+)".format(token),  r'\1' + color_sub(r'\2') + r'\3', s, 0, re.MULTILINE)
        return s

    @staticmethod
    def _get_old_path(file_path, metadata_path):
        if Path(metadata_path).exists():
            with open(metadata_path, 'r') as f:
                metadata = f.read()
            return search_meta_val(metadata, 'Old file path')
        else:
            logger.debug('No metadata found!')
            return file_path

    def _get_option(self, old_path):
        logger.info('Possible actions: ')
        for i, folder_path in enumerate(self.output_folders):
            if i == 0:
                msg = f"{bold(str(i))}/spb)"
            else:
                msg = f"{bold(str(i))})"
            logger.info(f" {msg}\t\tMove file and metadata to '{str(Path(folder_path))}'")
        if self.restore_original_base_dir:
            # TODO: important, normalize in interact()?
            logger.info(" {})\t\tRestore file with original path to '{}' and delete metadata".format(
                f"{bold('r')}", normalize("NFKC", f"{self.restore_original_base_dir.strip('/')}/{old_path}")))
        # TODO: use better formatting than relying on tabs
        # NOTE: SyntaxError: f-string expression part cannot include a backslash
        logger.info(" {})\t\tMove to another folder\t\t\t| {})\t\tInteractively reorganize the file".format(
            f"{bold('m/tab')}", f"{bold('i/bs')}"))
        logger.info(" {})\t\tOpen file in external viewer\t\t| {})\t\tRead in terminal".format(
            f"{bold('o/ent')}", f"{bold('l')}"))
        logger.info(" {})\t\tRead the saved metadata file\t\t| {})\t\tRun ebook-meta on the file".format(
            f"{bold('c')}", f"{bold('?')}"))
        logger.info(" {})\t\tRun shell in terminal\t\t\t| {})\t\tEval code (change env vars)".format(
            f"{bold('t/`')}", f"{bold('e')}"))
        logger.info(" {})\t\tSkip file\t\t\t\t| {})\tQuit".format(
            f"{bold('s')}", f"{bold('q/esc')}"))
        choice = getch()
        if choice == '\x7f':  # backspace
            logger.debug('i')
            choice = 'i'
        elif choice == '\t':  # horizontal tab
            logger.debug('m')
            choice = 'm'
        elif choice == ' ':  # space
            logger.debug('0')
            choice = '0'
        elif choice == '\r':  # null (for newline)
            logger.debug('o')
            choice = 'o'
        elif choice == '`':  # backtick
            logger.debug('t')
            choice = 't'
        elif choice == '\x1b':  # escape
            logger.debug('q')
            choice = 'q'
        elif choice == '\x03':  # ctrl+c
            logger.debug('ctrl+c (quitting)')
            raise SystemExit(blue('Quitting!'))
        return choice

    def _header_and_check(self, file_path, metadata_path):
        filename = Path(file_path).name
        filename = normalize("NFKC", filename)
        _, file_size = get_file_size(file_path, unit='MiB')
        msg_size = bold(file_size)
        msg = f"File\t\t'{filename}' ({msg_size} in '{Path(file_path).parent}')"
        if not Path(metadata_path).exists():
            logger.info(msg + bold(f"{red(' [no metadata]')}"))
            return 1
        logger.info(msg + bold(f" [has metadata]"))
        old_path = self._get_old_path(file_path, metadata_path)
        old_name = Path(old_path).name
        old_name = normalize("NFKC", old_name)
        similar_tokens = set()
        missing_tokens = set()
        partial_tokens = set()
        old_name_sub = re.sub(self.tokens_to_ignore, r'', Path(old_name).stem, 0, re.MULTILINE)
        # NOTE: not necessary to remove tokens in new filename?
        new_name_sub = re.sub(self.tokens_to_ignore, r'', Path(filename).stem, 0, re.MULTILINE)
        # old_tokens = re.findall(r"[^\W\d_]+|\d+", old_name_sub)
        # new_tokens = re.findall(r"[^\W\d_]+|\d+", new_name_sub)
        old_tokens = re.findall(r"[^\W\d_]+", old_name_sub)
        new_tokens = re.findall(r"[^\W\d_]+", new_name_sub)
        for old_token in old_tokens:
            cleaned_old_token = remove_diacritics(old_token.lower())
            found = False
            if len(cleaned_old_token) >= self.token_min_length:
                for new_token in new_tokens:
                    if cleaned_old_token in remove_diacritics(new_token.lower()):
                        # TODO: fix partial
                        # Physics (old) Metaphysics and Physics (new) -> Physics is partial (which shouldn't)
                        if False and len(cleaned_old_token) < len(new_token):
                            partial_tokens.add(old_token)
                        else:
                            similar_tokens.add(old_token)
                        found = True
                        break
                if not found:
                    missing_tokens.add(old_token)
        old_name_hl = copy(old_name)
        old_name_hl = self._color_tokens_in_string(old_name_hl, missing_tokens)  # red (default)
        old_name_hl = self._color_tokens_in_string(old_name_hl, similar_tokens, 'green')
        # NOTE: Alexander (new) and Grammars and Automata (old) --> and considered as partial
        # because found in Alexander (which should not)
        # old_name_hl = self._color_tokens_in_string(old_name_hl, partial_tokens, 'yellow')
        # NOTE: Only color the first three digits of year because parentheses capture them in regex
        # TODO: add parenthesis to whole regex but test organize_ebooks/lib.py since it makes use of it
        # old_name_hl = re.sub(get_re_year(), blue(r'\1'), old_name_hl, 0, re.MULTILINE)
        match = re.search(get_re_year(), old_name_hl)
        if match:
            old_name_hl = old_name_hl.replace(match.group(), blue(match.group()))
        else:
            logger.debug('No year found in old filename')
        old_name_hl = old_name_hl.replace('REDCODE', COLORS['RED'])
        old_name_hl = old_name_hl.replace('GREENCODE', COLORS['GREEN'])
        old_name_hl = old_name_hl.replace('NCCODE', COLORS['NC'])
        logger.info(f"Old name\t'{old_name_hl}'")
        if missing_tokens:
            logger.info('Missing words from the old file name: ' + bold(', '.join(sorted(missing_tokens))))
            return 2
        logger.info(bold('No missing words from the old filename in the new!'))
        if not self.quick_mode:
            return 3
        logger.info('Quick mode enabled, skipping to the next file')
        return 0

    def _move_or_link_file_and_maybe_meta(self, new_folder, file_path, metadata_path):
        filename = Path(file_path).name
        new_path = unique_filename(new_folder, filename)
        new_metadata_path = f'{new_path}.{self.output_metadata_extension}'
        # NOTE: they don't provide the last two params
        logger.info(f"Moving file '{file_path}' to '{new_path}'...")
        move_or_link_file(file_path, new_path, self.dry_run, self.symlink_only)
        if Path(metadata_path).exists():
            logger.info(f"Moving file '{metadata_path}' to '{new_metadata_path}'...")
            move_or_link_file(metadata_path, new_metadata_path, self.dry_run, self.symlink_only)

    def _reorganize_interactively(self, file_path):
        metadata_path = f'{file_path}.{self.output_metadata_extension}'
        file_folder = Path(file_path).parent
        old_path = self._get_old_path(file_path, metadata_path)
        fname = normalize("NFKC", Path(old_path).name)
        # filename must be within single quotes
        opt = rlinput("Enter search terms or 'new filename': ", f"{fname}")
        logger.info(f'Your choice: {opt}')
        if opt == '':
            return 1
        elif re.match("^\'.+\'$", opt):
            opt = opt.strip("'")
            logger.info(f"Renaming file to '{opt}', removing the old metadata if present and saving old "
                        "file path in the new metadata...")
            # NOTE: they don't use user's dry_run and symlink_only
            move_or_link_file(file_path, Path(file_folder).joinpath(opt), self.dry_run, self.symlink_only)
            if Path(metadata_path).exists() and not self.dry_run:
                remove_file(metadata_path)
            file_path = Path(file_folder).joinpath(opt)
            if self.dry_run:
                logger.debug("DRY RUN: not deleting old metadata nor saving new metadata")
            else:
                metadata_path = f'{file_path}.{self.output_metadata_extension}'
                with open(metadata_path, 'w') as f:
                    f.write(f'Old file path       : {old_path}')
            self._review_file(file_path)
            return 0
        tmpmfile = tempfile.mkstemp(suffix='.txt')[1]
        isbn = find_isbns(opt, isbn_ret_separator='\n')
        if isbn:
            # Only the first ISBN is chosen
            isbn = isbn.split()[0]
            logger.info("Fetching metadata from sources "
                        f"{ISBN_METADATA_FETCH_ORDER} for ISBN '{isbn}' into "
                        f"'{tmpmfile}'...")
            fetch_arg = f"--isbn='{isbn}'"
            fetch_sources = ISBN_METADATA_FETCH_ORDER
        else:
            logger.info("Fetching metadata from sources "
                        f"{ORGANIZE_WITHOUT_ISBN_SOURCES} for title '{opt}' "
                        f"into '{tmpmfile}'...")
            fetch_arg = "--title='$opt'"
            fetch_sources = ORGANIZE_WITHOUT_ISBN_SOURCES
        for fetch_source in fetch_sources:
            logger.info(f"Fetching metadata from '{fetch_source}' sources...")
            result = fetch_metadata(fetch_source, fetch_arg)
            metadata = result.stdout
            if metadata:
                # Not adding [meta] before each line like they do
                with open(tmpmfile, 'w') as f:
                    f.write(metadata)
                time.sleep(0.1)
                logger.info('Successfully fetched metadata: ')
                # TODO: add in function metadata wrap lines
                for line in metadata.splitlines(1):
                    for i, wrapped_line in enumerate(wrap(line, 100)):
                        if i > 0:
                            wrapped_line = f'  {wrapped_line}'
                        logger.info(f'[meta] {wrapped_line}'.strip())
                opt = rlinput('Do you want to use these metadata to rename the file (y/n/Q): ')
                if opt in ['y', 'Y']:
                    logger.info(blue('You chose yes, renaming the file...'))
                elif opt in ['n', 'N']:
                    logger.info(blue('You chose no, trying the next metadata source...'))
                    continue
                elif opt in ['q', 'Q']:
                    logger.info(blue('You chose to quit, returning to the main menu!'))
                    break
                else:
                    logger.info(f"Invalid choice '{opt}', returning to the main menu!")
                    break
                if Path(metadata_path).exists():
                    logger.info(f"Removing old metadata file '{metadata_path}'...")
                    if self.dry_run:
                        logger.debug('DRY RUN: old metadata will not be deleted!')
                    else:
                        remove_file(metadata_path)
                logger.debug('Adding additional metadata to the end of the metadata file...')
                more_metadata = 'Old file path       : {}\n' \
                                'Metadata source     : {}\n'.format(file_path, fetch_source)
                logger.debug(more_metadata)
                with open(tmpmfile, 'a') as f:
                    f.write(more_metadata)
                if isbn == '':
                    isbn = find_isbns(metadata, isbn_ret_separator=' - ')
                if isbn:
                    with open(tmpmfile, 'a') as f:
                        f.write(f'ISBN                : {isbn}')
                logger.debug(f"Organizing '{file_path}' (with '{tmpmfile}')...")
                # NOTE: They don't provide dry_run and next parameters
                file_path = move_or_link_ebook_file_and_metadata(
                    file_folder, file_path, tmpmfile, dry_run=self.dry_run,
                    keep_metadata=True,
                    output_metadata_extension=self.output_metadata_extension,
                    symlink_only=self.symlink_only)
                logger.debug(f"New path is '{file_path}'! Reviewing the new file...")
                self._review_file(file_path)
                # NOTE: they forgot to remove tmp file since they do a return and not a break
                break
        logger.debug(f"Removing temp file '{tmpmfile}'...")
        remove_file(tmpmfile)
        return 0

    def _review_file(self, file_path):
        metadata_path = f'{file_path}.{self.output_metadata_extension}'
        while self._header_and_check(file_path, metadata_path):
            try:
                old_path = self._get_old_path(file_path, metadata_path)
                opt = self._get_option(old_path)
                logger.info(f'Chosen option: {opt}')
                if opt.isdigit() and int(opt) in range(0, 10):
                    opt = int(opt)
                    if opt < len(self.output_folders):
                        self._move_or_link_file_and_maybe_meta(self.output_folders[opt], file_path, metadata_path)
                        return 0
                    else:
                        logger.warning(yellow(f'Invalid output path {opt}!'))
                elif opt in ['m', 'r']:
                    new_path_default = ''
                    if opt == 'm':
                        if self.custom_move_base_dir:
                            new_path_default = self.custom_move_base_dir
                        else:
                            logger.warning(yellow('`custom-move-base-dir` is empty!'))
                    else:
                        # Both alternatives don't work
                        # 1: //Users/test/test_organize/input_folder/filename.djvu
                        # new_path_default = str(Path(self.restore_original_base_dir).joinpath('/' + old_path))
                        # 2: /Users/test/test_organize/input_folder/filename.djvu
                        # new_path_default = os.path.join(self.restore_original_base_dir, '/', old_path)
                        # Remove last '/' if that is the case
                        # TODO: do it in interact()
                        if self.restore_original_base_dir:
                            # Remove '/' at the end
                            new_path_default = f"{self.restore_original_base_dir.strip('/')}/{old_path}"
                        else:
                            logger.warning(yellow('`restore-original-base-dir` is empty!'))
                    new_path = rlinput('Delete metadata if it exists and move the file to: ', new_path_default)
                    if new_path:
                        if Path(new_path).suffix:
                            if self.dry_run:
                                logger.debug('DRY RUN: metadata will not be deleted and file will not be moved!')
                            else:
                                # parents=True (create all folders along the path)
                                # exists_ok=True (no error if folders already exist)
                                Path(new_path).parent.mkdir(parents=True, exist_ok=True)
                                # clobber=True (in move) by default
                                move(file_path, new_path)
                                if Path(metadata_path).exists():
                                    remove_file(metadata_path)
                                return 0
                        else:
                            logger.warning(yellow("You didn't entered a file path (with extension)!"))
                    else:
                        logger.warning(yellow('No path entered, ignoring!'))
                elif opt in ['i']:
                    self._reorganize_interactively(file_path)
                elif opt in ['o']:
                    logger.info(blue('Opening the document...'))
                    result = open_document(file_path)
                    if result.returncode:
                        logger.error(red(f'{result.stderr}.strip()'))
                elif opt in ['l']:
                    open_with_less(file_path, **self.__dict__)
                elif opt in ['c']:
                    if Path(metadata_path).exists():
                        with open(metadata_path, 'r') as f:
                            metadata = f.read()
                        # TODO: add in function metadata wrap lines
                        for line in metadata.splitlines(1):
                            for i, wrapped_line in enumerate(wrap(line, 100)):
                                # logger.info('\t' + wrapped_line)
                                if i > 0:
                                    wrapped_line = '   ' + wrapped_line.strip()
                                logger.info('\t' + wrapped_line)
                    else:
                        logger.warning(yellow('There is no metadata file present!'))
                elif opt in ['?']:
                    logger.info('Starting ebook-meta...')
                    result = get_ebook_metadata(file_path)
                    # TODO: result.stderr? if returncode!=0?
                    logger.debug(f'returncode: {result.returncode}')
                    # TODO: add in function metadata wrap lines
                    for line in result.stdout.splitlines(1):
                        for i, wrapped_line in enumerate(wrap(line, 100)):
                            # logger.info('\t' + wrapped_line)
                            if i > 0:
                                wrapped_line = '   ' + wrapped_line.strip()
                            logger.info('\t' + wrapped_line)
                elif opt in ['e']:
                    evals = rlinput('Evaluate: TOKENS_TO_IGNORE=', f"{self.tokens_to_ignore}")
                    if evals:
                        self.tokens_to_ignore = evals
                elif opt in ['t']:
                    logger.info("Launching 'bash'...")
                    subprocess.call(['bash'], shell=True)
                elif opt in ['s']:
                    logger.info(blue('Skipping the file!'))
                    return 0
                elif opt in ['q']:
                    logger.debug('Quitting')
                    raise SystemExit(blue('Quitting!'))
            except KeyboardInterrupt:
                logger.debug('Detected ctrl+c!')
                logger.info('')
            logger.info('')
        # Quick mode was enabled and the file looked ok!
        # NOTE: they don't check the case where output_folders is empty
        if self.output_folders:
            self._move_or_link_file_and_maybe_meta(self.output_folders[0], file_path, metadata_path)
        else:
            logger.warning(yellow('Quick mode is enabled but no output folders (`-o` option) were specified!'))
            # NOTE: return 1?
        return 0

    def _update(self, **kwargs):
        logger.debug('Updating attributes for organizer...')
        for k, v in self.__dict__.items():
            new_val = kwargs.get(k)
            if new_val and v != new_val:
                logger.debug(f'{k}: {v} -> {new_val}')
                self.__setattr__(k, new_val)

    def interact(self, folder_to_organize, output_folders=None, **kwargs):
        if folder_to_organize is None:
            logger.error(red("\nerror: the following arguments are required: folder_to_organize"))
            return 1
        if not Path(folder_to_organize).exists():
            logger.error(red(f"Input folder doesn't exist: {folder_to_organize}"))
            return 1
        self.folder_to_organize = folder_to_organize
        self.output_folders = output_folders
        if self.output_folders is None:
            self.output_folders = []
        self._update(**kwargs)
        files = []
        if is_dir_empty(folder_to_organize):
            logger.warning(yellow(f'Folder is empty: {folder_to_organize}'))
        logger.debug(f"Recursively scanning '{folder_to_organize}' for files "
                     f"(except .{self.output_metadata_extension})...")
        for fp in Path(folder_to_organize).rglob('*'):
            # Ignore directory and hidden files
            if Path.is_file(fp) and not fp.name.startswith('.') and \
                    not fp.name.endswith(self.output_metadata_extension):
                # logger.debug(f"{fp.name}")
                files.append(fp)
        if not files:
            logger.warning(yellow(f'No ebooks found in folder: {folder_to_organize}'))
            return 0
        files.sort(key=lambda x: x.name)
        logger.info('=====================================================')
        for fp in files:
            self._review_file(fp)
            logger.info('=====================================================')
        logger.info(blue('No more ebooks to organize!'))
        return 0


organizer = InteractiveOrganizer()
