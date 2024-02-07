""""Interactively and manually organize ebook files quickly.

This is a Python port of `interactive-organizer.sh` from `ebook-tools` written in
shell by `na--`.

Ref.: https://github.com/na--/ebook-tools
"""
import argparse
import codecs
import logging
import os

# TODO
# __version__ = '0.1.0'
from interactive_organizer import __version__, lib
# import lib
from interactive_organizer.lib import namespace_to_dict, setup_log, blue, green, red, yellow
# from lib import namespace_to_dict, setup_log, blue, green, red, yellow

# import ipdb

logger = logging.getLogger('interactive_script')
logger.setLevel(logging.CRITICAL + 1)

# =====================
# Default config values
# =====================

# Misc options
# ============
QUIET = False
OUTPUT_FILE = 'output.txt'


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        print_(self.format_usage().splitlines()[0])
        self.exit(2, red(f'\nerror: {message}\n'))


class MyFormatter(argparse.HelpFormatter):
    """
    Corrected _max_action_length for the indenting of subactions
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for subaction in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))
            # print_('inv', invocations)

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    # Ref.: https://stackoverflow.com/a/23941599/14664104
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)


class OptionsChecker:
    def __init__(self, add_opts, remove_opts):
        self.add_opts = init_list(add_opts)
        self.remove_opts = init_list(remove_opts)

    def check(self, opt_name):
        return not self.remove_opts.count(opt_name) or \
               self.add_opts.count(opt_name)


# General options
def add_general_options(parser, add_opts=None, remove_opts=None,
                        program_version=__version__,
                        title='General options'):
    checker = OptionsChecker(add_opts, remove_opts)
    parser_general_group = parser.add_argument_group(title=title)
    if checker.check('help'):
        parser_general_group.add_argument('-h', '--help', action='help',
                                          help='Show this help message and exit.')
    if checker.check('version'):
        parser_general_group.add_argument(
            '-v', '--version', action='version',
            version=f'%(prog)s v{program_version}',
            help="Show program's version number and exit.")
    if checker.check('quiet'):
        parser_general_group.add_argument(
            '-q', '--quiet', action='store_true',
            help='Enable quiet mode, i.e. nothing will be printed.')
    if checker.check('verbose'):
        parser_general_group.add_argument(
            '--verbose', action='store_true',
            help='Print various debugging information, e.g. print traceback '
                 'when there is an exception.')
    if checker.check('dry-run'):
        parser_general_group.add_argument(
            '-d', '--dry-run', dest='dry_run', action='store_true',
            help='If this is enabled, no file rename/move/symlink/etc. '
                 'operations will actually be executed.')
    if checker.check('symlink-only'):
        parser_general_group.add_argument(
            '-s', '--symlink-only', dest='symlink_only', action='store_true',
            help='Instead of moving the ebook files, create symbolic links to '
                 'them.')
    if checker.check('log-level'):
        parser_general_group.add_argument(
            '--log-level', dest='logging_level',
            choices=['debug', 'info', 'warning', 'error'], default=lib.LOGGING_LEVEL,
            help='Set logging level.' + get_default_message(lib.LOGGING_LEVEL))
    if checker.check('log-format'):
        parser_general_group.add_argument(
            '--log-format', dest='logging_formatter',
            choices=['console', 'only_msg', 'simple',], default=lib.LOGGING_FORMATTER,
            help='Set logging formatter.' + get_default_message(lib.LOGGING_FORMATTER))
    return parser_general_group


# Ref.: https://stackoverflow.com/a/5187097/14664104
def decode(value):
    return codecs.decode(value, 'unicode_escape')


def get_default_message(default_value):
    return green(f' (default: {default_value})')


def init_list(list_):
    return [] if list_ is None else list_


def print_(msg):
    global QUIET
    if not QUIET:
        print(msg)


# Ref.: https://stackoverflow.com/a/4195302/14664104
def required_length(nmin, nmax, is_list=True):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if isinstance(values, str):
                tmp_values = [values]
            else:
                tmp_values = values
            if not nmin <= len(tmp_values) <= nmax:
                if nmin == nmax:
                    msg = 'argument "{f}" requires {nmin} arguments'.format(
                        f=self.dest, nmin=nmin, nmax=nmax)
                else:
                    msg = 'argument "{f}" requires between {nmin} and {nmax} ' \
                          'arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


def setup_argparser():
    width = os.get_terminal_size().columns - 5
    name_input = 'folder_to_organize'
    usage_msg = blue(f"%(prog)s [OPTIONS] {{{name_input}}} -o {{{'output_folder'}}} [{{{'output_folder'}}}]")
    desc_msg = 'Interactively and manually organize ebook files quickly.\n\n' \
               'This script is based on the great ebook-tools written in shell ' \
               'by na-- (See https://github.com/na--/ebook-tools).'
    parser = ArgumentParser(
        description="",
        usage=f"{usage_msg}\n\n{desc_msg}",
        add_help=False,
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=50, width=width))
    general_group = add_general_options(
        parser,
        remove_opts=[],
        program_version=__version__,
        title=yellow('General options'))
    # ======================
    # Convert-to-txt options
    # ======================
    convert_group = parser.add_argument_group(title=yellow('Convert-to-txt options'))
    convert_group.add_argument(
        '--djvu', dest='djvu_convert_method',
        choices=['djvutxt', 'ebook-convert'], default=lib.DJVU_CONVERT_METHOD,
        help='Set the conversion method for djvu documents.'
             + get_default_message(lib.DJVU_CONVERT_METHOD))
    convert_group.add_argument(
        '--epub', dest='epub_convert_method',
        choices=['epubtxt', 'ebook-convert'], default=lib.EPUB_CONVERT_METHOD,
        help='Set the conversion method for epub documents.'
             + get_default_message(lib.EPUB_CONVERT_METHOD))
    convert_group.add_argument(
        '--msword', dest='msword_convert_method',
        choices=['catdoc', 'textutil', 'ebook-convert'], default=lib.MSWORD_CONVERT_METHOD,
        help='Set the conversion method for epub documents.'
             + get_default_message(lib.MSWORD_CONVERT_METHOD))
    convert_group.add_argument(
        '--pdf', dest='pdf_convert_method',
        choices=['pdftotext', 'ebook-convert'], default=lib.PDF_CONVERT_METHOD,
        help='Set the conversion method for pdf documents.'
             + get_default_message(lib.PDF_CONVERT_METHOD))
    # ===================
    # Interactive options
    # ===================
    interactive_group = parser.add_argument_group(title=yellow('Interactive options'))
    interactive_group.add_argument(
        "--qm", "--quick-mode", dest='quick_mode', action="store_true",
        help='This mode is useful when `organize_ebooks` was called with '
             '`--keep-metadata`. Ebooks that contain all of the tokens from '
             'the old file name in the new one are directly moved to the '
             'default output folder.')
    interactive_group.add_argument(
        '--token-min-length', dest='token_min_length', metavar='LENGTH',
        type=int,
        help='''When files and file metadata are parsed, they are split into
            words and ones shorter than this value are ignored. By default, single and two
            character number and words are ignored.'''
             + get_default_message(lib.TOKEN_MIN_LENGTH))
    interactive_group.add_argument(
        '--tokens-to-ignore', dest='tokens_to_ignore', metavar='TOKENS',
        help='''A regular expression that is matched against the
            filename/author/title tokens and matching tokens are ignored. The
            default regular expression includes common words that probably hinder
            online metadata searching like book, novel, series, volume and others,
            as well as probable publication years like (so 1999 is ignored while
            2033 is not).'''
             + get_default_message(lib.TOKENS_TO_IGNORE))
    interactive_group.add_argument(
        "-m", "---metadata-fetch-order", nargs='+',
        dest='isbn_metadata_fetch_order', metavar='METADATA_SOURCE',
        help='''This option allows you to specify the online metadata
                sources and order in which the subcommands will try searching in
                them for books by their ISBN. The actual search is done by
                calibre's `fetch-ebook-metadata` command-line application, so any
                custom calibre metadata plugins can also be used. To see the
                currently available options, run `fetch-ebook-metadata --help` and
                check the description for the `--allowed-plugin` option. If you use
                Calibre versions that are older than 2.84, it's required to
                manually set this option to an empty string.'''
             + get_default_message(lib.ISBN_METADATA_FETCH_ORDER))
    interactive_group.add_argument(
        '--owis', '--organize-without-isbn-sources', nargs='+',
        dest='organize_without_isbn_sources', metavar='METADATA_SOURCE',
        default=lib.ORGANIZE_WITHOUT_ISBN_SOURCES,
        help='''This option allows you to specify the online metadata sources
            in which the script will try searching for books by non-ISBN
            metadata (i.e. author and title). The actual search is done by
            calibre's `fetch-ebook-metadata` command-line application, so any
            custom calibre metadata plugins can also be used. To see the currently
            available options, run `fetch-ebook-metadata --help` and check the
            description for the `--allowed-plugin` option. Because Calibre versions
            older than 2.84 don't support the `--allowed-plugin` option, if you
            want to use such an old Calibre version you should manually set
            `organize_without_isbn_sources` to an empty string.'''
             + get_default_message(lib.ORGANIZE_WITHOUT_ISBN_SOURCES))
    # It is hardcoded, no custom support
    """
    interactive_group.add_argument(
        "--ddm", "--diacritic-difference-masking",
        dest='diacritic_difference_masking', default=lib.DIACRITIC_DIFFERENCE_MASKINGS,
        help='Which differences due to accents and other diacritical marks to '
             'be ignored when comparing tokens in `quick-mode` and the '
             'interactive interface. The default value handles some basic '
             'cases like allowing letters like á, à, â and others instead of a '
             'and the reverse when comparing the old and new files.'
             + get_default_message(lib.DIACRITIC_DIFFERENCE_MASKINGS))
    """
    # NOTE: they don't seem to make use of it
    """
    interactive_group.add_argument(
        "-m", "--match-partial-words", dest='match_partial_words',
        action="store_true",
        help='Whether tokens from the old filenames that partially match in '
             'the new filename to be accepted by `quick-mode` and the '
             'interactive interface.')
    """
    # ====================
    # Input/Output options
    # ====================
    input_output_group = parser.add_argument_group(title=yellow('Input/Output options'))
    input_output_group.add_argument(
        name_input,
        help='Folder containing the ebook files that need to be organized.')
    input_output_group.add_argument(
        '-o', '--output-folders', dest='output_folders', metavar='PATH', nargs='*',
        help='The different output folders to which you can quickly move ebook files. '
             'The first specified folder is the default.')
    input_output_group.add_argument(
        '-c', '--custom-move-base-dir', dest='custom_move_base_dir', metavar='PATH',
        default=lib.CUSTOM_MOVE_BASE_DIR,
        help='A base directory in whose sub-folders files can more easily be '
             'moved during the interactive session because of tab autocompletion.'
             + get_default_message(lib.CUSTOM_MOVE_BASE_DIR))
    input_output_group.add_argument(
        '-r', '--restore-original-base-dir', dest='restore_original_base_dir',
        metavar='PATH', default=lib.RESTORE_ORIGINAL_BASE_DIR,
        help='If you want to enable the option of restoring files to their '
             'original folders (or at least with the same folder structure), '
             'set this as the base path.'
             + get_default_message(lib.RESTORE_ORIGINAL_BASE_DIR))
    input_output_group.add_argument(
        '--oft', '--output-filename-template', dest='output_filename_template',
        metavar='TEMPLATE',
        help='''This specifies how the filenames of the organized files will
                look. It is a bash string that is evaluated so it can be very flexible
                (and also potentially unsafe).''' +
             get_default_message(lib.OUTPUT_FILENAME_TEMPLATE))
    input_output_group.add_argument(
        '--ome', '--output-metadata-extension', dest='output_metadata_extension',
        metavar='EXTENSION',
        help='''This is the extension of the additional metadata file that is 
        saved next to each newly renamed file.'''
             + get_default_message(lib.OUTPUT_METADATA_EXTENSION))
    return parser


def show_exit_code(exit_code):
    msg = f'Program exited with {exit_code}'
    if exit_code == 1:
        logger.error(red(f'{msg}'))
    else:
        logger.debug(msg)


def main():
    global QUIET
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        QUIET = args.quiet
        setup_log(args.quiet, args.verbose, args.logging_level, args.logging_formatter,
                  logger_names=['interactive_script', 'interactive_lib', 'organize_lib'])
        # Actions
        args_dict = namespace_to_dict(args)
        exit_code = lib.organizer.interact(**args_dict)
    except KeyboardInterrupt:
        # Loggers might not be setup at this point
        print_(yellow('\nProgram stopped!'))
        exit_code = 2
    except Exception as e:
        print_(red('Program interrupted!'))
        print_(red(str(e)))
        logger.exception(e)
        exit_code = 1
    if __name__ != '__main__':
        show_exit_code(exit_code)
    return exit_code


if __name__ == '__main__':
    retcode = main()
    show_exit_code(retcode)
