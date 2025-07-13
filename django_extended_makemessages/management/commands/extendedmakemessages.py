try:
    from typing import override
except ImportError:

    def override(func):
        return func


import ast
import difflib
import json
import re

from argparse import RawDescriptionHelpFormatter
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from sys import exit

from django.core.management import ManagementUtility
from django.core.management.base import CommandError, CommandParser, DjangoHelpFormatter
from django.core.management.commands.makemessages import Command as MakeMessagesCommand

import django_extended_makemessages


IMPORT_ALIAS_IGNORED_FOLDERS = {
    "lib",
    "site-packages",
}

GETTEXT_FUNCTION_NAMES = {
    "gettext_lazy",
    "gettext_noop",
    "gettext",
    "ngettext_lazy",
    "ngettext",
    "npgettext_lazy",
    "npgettext",
    "pgettext_lazy",
    "pgettext",
}

PO_FILE_HEADER_PATTERN = re.compile(
    r"^msgid +\"\"\nmsgstr +\"[^\n]*\"(?:\n *\"[^\n]*\")*", re.MULTILINE
)

PO_FILE_ENTRY_PATTERN = re.compile(
    (
        r"(^msgctxt +\"[^\n]*\"(?:\n *\"[^\n]*\")*\n)?"
        r"(^msgid +(?P<msgid>\"[^\n]*\"(?:\n *\"[^\n]*\")*)\n)"
        r"(^msgid_plural +\"[^\n]*\"(?:\n *\"[^\n]*\")*\n)?"
        r"((?:^msgstr(?:\[\d+\])? +\"[^\n]*\"(?:\n *\"[^\n]*\")*\n)+)"
    ),
    re.MULTILINE,
)

PO_FILE_UNTRANSLATED_MSGSTR_PATTERN = re.compile(
    r"^(?P<msgstr>msgstr(?:\[\d+\])?) +\"\"(?!\n *\")", re.MULTILINE
)

NOT_PROVIDED = object()


def get_gettext_import_aliases(root_path: Path) -> "dict[str, set[str]]":
    aliases: "dict[str, set[str]]" = defaultdict(set)

    def is_inside_ignored_folders(file: Path) -> bool:
        return bool(
            set(file.relative_to(Path.cwd()).parts).intersection(
                IMPORT_ALIAS_IGNORED_FOLDERS
            )
        )

    files = (
        file for file in root_path.rglob("*.py") if not is_inside_ignored_folders(file)
    )

    for file in files:
        content = file.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file.relative_to(Path.cwd())))

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            if node.module != "django.utils.translation":
                continue

            for alias in node.names:
                if alias.name not in GETTEXT_FUNCTION_NAMES:
                    continue

                # e.g. from django.utils.translation import gettext
                if alias.asname is None:
                    continue

                # e.g. from django.utils.translation import gettext as gt
                else:
                    aliases[alias.name].add(alias.asname)

    return aliases


def get_argnums(function: str):
    if function in ("gettext", "gettext_lazy", "gettext_noop"):
        return "1"
    if function in ("ngettext", "ngettext_lazy"):
        return "1,2"
    if function in ("npgettext", "npgettext_lazy"):
        return "1c,2,3"
    if function in ("pgettext", "pgettext_lazy"):
        return "1c,2"

    raise ValueError(f"Unknown gettext function: {function}")


def parse_multiline_string(string: str) -> str:
    return "".join(json.loads("[" + string.replace("\n", ",") + "]"))


def get_untranslated_msgstrs(pofile: Path) -> "set[tuple[Path, int, str, str]]":
    untranslated_msgstrs = set()

    for entry_match in PO_FILE_ENTRY_PATTERN.finditer(pofile.read_text()):
        entry = entry_match.group()

        for untranslated_msgstr_match in PO_FILE_UNTRANSLATED_MSGSTR_PATTERN.finditer(
            entry
        ):
            offset = entry_match.start() + untranslated_msgstr_match.start()
            line_number = pofile.read_text().count("\n", 0, offset) + 1

            untranslated_msgstr = untranslated_msgstr_match.group("msgstr")
            untranslated_msgid = parse_multiline_string(entry_match.group("msgid"))

            untranslated_msgstrs.add(
                (pofile, line_number, untranslated_msgstr, untranslated_msgid)
            )

    return untranslated_msgstrs


class DjangoExtendedMakeMessagesHelpFormatter(
    DjangoHelpFormatter, RawDescriptionHelpFormatter
): ...


class Command(MakeMessagesCommand):

    help = MakeMessagesCommand.help + (
        "\n\n"
        "In addition to the options available in Django's makemessages command, this command "
        "exposes selected msgmerge/msguniq/msgattrib/xgettext options that make sense for usage "
        "in a Django project."
        "\n\n"
        "On top of that, this command also includes some custom options, which further simplify "
        "managing translations, but are not part of GNU gettext tools."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.untranslated_messages: "set[tuple[Path, int, str, str]]" = set()

    @override
    def run_from_argv(self, argv: "list[str]") -> None:
        self.prog_name = argv[0]
        super().run_from_argv(argv)

    @override
    def get_version(self) -> str:
        """Return the version of the `extendedmakemessages` command."""
        return django_extended_makemessages.__version__

    @override
    def create_parser(self, prog_name: str, subcommand: str, **kwargs):
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.formatter_class = DjangoExtendedMakeMessagesHelpFormatter
        return parser

    @override
    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)

        # Command specific options
        parser.add_argument(
            "--no-fuzzy-matching",
            action="store_true",
            help="Do not use fuzzy matching when an exact match is not found. This may speed up the operation considerably.",
        )
        parser.add_argument(
            "--add-comments",
            metavar="TAG",
            nargs="?",
            const=NOT_PROVIDED,
            action="append",
            help=(
                "Place comment blocks starting with tag and preceding keyword lines in the output file. Without a tag, the option"
                " means to put all comment blocks preceding keyword lines in the output file."
            ),
        )
        parser.add_argument(
            "--extract-all",
            action="store_true",
            help="Extract all strings.",
        )
        parser.add_argument(
            "--keyword",
            nargs="?",
            const=NOT_PROVIDED,
            action="append",
            help="Specify keywordspec as an additional keyword to be looked for. Without a keywordspec, the option means to not use default keywords.",
        )

        # Common options
        parser.add_argument(
            "--force-po",
            action="store_true",
            help="Always write an output file even if no message is defined.",
        )
        parser.add_argument(
            "--indent",
            action="store_true",
            help="Write the .po file using indented style.",
        )
        parser.add_argument(
            "--width",
            type=int,
            action="store",
            help="Set the output page width. Long strings in the output files will be split across multiple lines in order to ensure that each line's width (= number of screen columns) is less or equal to the given number.",
        )
        sort_group = parser.add_mutually_exclusive_group()
        sort_group.add_argument(
            "--sort-output",
            action="store_true",
            help="Generate sorted output.",
        )
        sort_group.add_argument(
            "--sort-by-file",
            action="store_true",
            help="Sort output by file location.",
        )

        # Custom options
        parser.add_argument(
            "--detect-aliases",
            action="store_true",
            help="Detect gettext functions aliases in the project and add them as keywords to xgettext command.",
        )
        parser.add_argument(
            "--show-untranslated",
            action="store_true",
            help="Show number of untranslated messages and, in more verbose mode, their location in .po files.",
        )
        parser.add_argument(
            "--keep-header",
            action="store_true",
            help="Keep the header of the .po file exactly the same as it was before the command was run. Do nothing if the .po file does not exist.",
        )
        parser.add_argument(
            "--no-flags",
            action="store_true",
            help="Don't write '#, flags' lines.",
        )
        parser.add_argument(
            "--no-flag",
            action="append",
            choices=(
                "fuzzy",
                "python-format",
                "python-brace-format",
                "no-python-format",
                "no-python-brace-format",
            ),
            help="Remove specific flag from the '#, flags' lines.",
        )
        parser.add_argument(
            "--no-previous",
            action="store_true",
            help="Don't write '#| previous' lines.",
        )
        parser.add_argument(
            "--no-untranslated",
            action="store_true",
            help="Exit with a non-zero status if any untranslated messages are found in any .po file.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit with a non-zero status if any .po file would be added or changed. Implies --dry-run.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Restore the .po file to its original state after running the command.",
        )
        parser.add_argument(
            "--compile",
            action="store_true",
            help="Compile .po files to .mo files after running the command.",
        )

    @override
    def handle(self, *args, **options):
        self.options = options
        options["ignore_patterns_without_default"] = options["ignore_patterns"][:]
        options["track_untranslated"] = (
            options["show_untranslated"] or options["no_untranslated"]
        )

        if options["check"]:
            options["dry_run"] = True

        # Command specific options
        if options["no_fuzzy_matching"]:
            self.msgmerge_options.append("--no-fuzzy-matching")
        if options["add_comments"]:
            assert isinstance(options["add_comments"], list)

            # Put all comment blocks preceding keyword lines in the output file
            if NOT_PROVIDED in options["add_comments"]:
                self.xgettext_options.append("--add-comments")

            # Place comment blocks starting with tag and preceding keyword lines in the output file
            self.xgettext_options += [
                f"--add-comments={tag}"
                for tag in options["add_comments"]
                if isinstance(tag, str)
            ]
        if options["extract_all"]:
            self.xgettext_options.append("--extract-all")
        if options["keyword"] is not None:
            assert isinstance(options["keyword"], list)

            # Remove default keywords
            if NOT_PROVIDED in options["keyword"]:
                self.xgettext_options.append("--keyword")

            # Add custom keywords
            self.xgettext_options += [
                f"--keyword={keywordspec}"
                for keywordspec in options["keyword"]
                if isinstance(keywordspec, str)
            ]

        # Common options
        if options["force_po"]:
            self.msgmerge_options.append("--force-po")
            self.msguniq_options.append("--force-po")
            self.msgattrib_options.append("--force-po")
            self.xgettext_options.append("--force-po")
        if options["indent"]:
            self.msgmerge_options.append("--indent")
            self.msguniq_options.append("--indent")
            self.msgattrib_options.append("--indent")
            self.xgettext_options.append("--indent")
        if options["width"]:
            self.msgmerge_options.append(f"--width={options['width']}")
            self.msguniq_options.append(f"--width={options['width']}")
            self.msgattrib_options.append(f"--width={options['width']}")
            self.xgettext_options.append(f"--width={options['width']}")
        if options["sort_output"]:
            self.msgmerge_options.append("--sort-output")
            self.msguniq_options.append("--sort-output")
            self.msgattrib_options.append("--sort-output")
            self.xgettext_options.append("--sort-output")
        if options["sort_by_file"]:
            self.msgmerge_options.append("--sort-by-file")
            self.msguniq_options.append("--sort-by-file")
            self.msgattrib_options.append("--sort-by-file")
            self.xgettext_options.append("--sort-by-file")

        # Custom options
        if options["detect_aliases"]:
            self.xgettext_options += [
                f"--keyword={alias}:{get_argnums(function)}"
                for function, aliases in get_gettext_import_aliases(Path.cwd()).items()
                for alias in aliases
            ]

        super().handle(*args, **options)

        if options["compile"]:
            compilemessages_argv = [self.prog_name, "compilemessages"]

            # Multiple values options
            for option in ["exclude", "locale"]:
                for value in options[option]:
                    compilemessages_argv.extend([f"--{option}", str(value)])

            for value in options["ignore_patterns_without_default"]:
                compilemessages_argv.extend(["--ignore", str(value)])

            # Single value options
            for option in ["verbosity", "settings", "pythonpath"]:
                if options[option]:
                    compilemessages_argv.extend([f"--{option}", str(options[option])])

            # True/False options
            for option in ["traceback", "no_color", "force_color"]:
                if options[option]:
                    compilemessages_argv.append(f"--{option.replace('_', '-')}")

            ManagementUtility(compilemessages_argv).execute()

        if options["show_untranslated"] and self.untranslated_messages:
            unique_po_files = set(message[0] for message in self.untranslated_messages)

            self.stdout.write(
                f"{len(self.untranslated_messages)} untranslated message{'s' if len(self.untranslated_messages) > 1 else ''}"
                + f" in {len(unique_po_files)} .po file{'s' if len(unique_po_files) > 1 else ''}"
            )

            if self.verbosity > 1:
                for pofile, line_number, msgstr, msgid in sorted(
                    self.untranslated_messages
                ):
                    self.stdout.write(
                        f"untranslated {msgstr} {pofile}:{line_number} {repr(msgid)}"
                    )

    @override
    def write_po_file(self, potfile: str, locale: str):
        pofile = (
            Path(potfile)
            .parent.joinpath(locale, "LC_MESSAGES", f"{self.domain}.po")
            .absolute()
        )

        if self.options["check"]:
            if pofile.exists():
                if self.verbosity > 1:
                    pofile_content_before_write = pofile.read_text(encoding="utf-8")
                pofile_digest_before_write = sha256(pofile.read_bytes()).hexdigest()
            else:
                self.stderr.write(f"File {pofile} added. [--check]")
                exit(1)

        if self.options["dry_run"]:
            original_pofile_content = (
                pofile.read_text(encoding="utf-8") if pofile.exists() else None
            )

        if pofile.exists() and self.options["keep_header"]:
            header_match = PO_FILE_HEADER_PATTERN.search(
                pofile.read_text(encoding="utf-8")
            )
            header_to_keep = header_match.group() if header_match else None
        else:
            header_to_keep = None

        try:
            super().write_po_file(potfile, locale)
        except CommandError as error:
            if self.options["dry_run"]:
                if original_pofile_content is None:
                    pofile.unlink()
                else:
                    pofile.write_text(original_pofile_content, encoding="utf-8")

            raise error

        if self.options["keep_header"] and header_to_keep is not None:
            pofile.write_text(
                PO_FILE_HEADER_PATTERN.sub(
                    header_to_keep.replace("\\", "\\\\"),  # Double escape for re.sub
                    pofile.read_text(),
                ),
                encoding="utf-8",
            )

        if self.options["no_flags"]:
            lines = pofile.read_text(encoding="utf-8").split("\n")
            lines_without_flags = (line for line in lines if not line.startswith("#, "))
            pofile.write_text("\n".join(lines_without_flags), encoding="utf-8")

        elif self.options["no_flag"]:
            assert isinstance(self.options["no_flag"], list)

            for flag in self.options["no_flag"]:
                lines = pofile.read_text(encoding="utf-8").split("\n")
                lines_without_flag = (
                    line.replace(f", {flag}", "")
                    for line in lines
                    if line != f"#, {flag}"
                )
                pofile.write_text("\n".join(lines_without_flag), encoding="utf-8")

        if self.options["no_previous"]:
            lines = pofile.read_text(encoding="utf-8").split("\n")
            lines_without_previous = (
                line for line in lines if not line.startswith("#, ")
            )
            pofile.write_text("\n".join(lines_without_previous), encoding="utf-8")

        if self.options["check"]:
            if self.verbosity > 1:
                pofile_content_after_write = pofile.read_text(encoding="utf-8")
            pofile_digest_after_write = sha256(pofile.read_bytes()).hexdigest()
            pofile_changed = pofile_digest_before_write != pofile_digest_after_write

        if self.options["track_untranslated"]:
            self.untranslated_messages.update(get_untranslated_msgstrs(pofile))

        if self.options["dry_run"]:
            if original_pofile_content is None:
                pofile.unlink()
            else:
                pofile.write_text(original_pofile_content, encoding="utf-8")

        if self.options["no_untranslated"] and self.untranslated_messages:
            pofile, line_number, msgstr, msgid = sorted(self.untranslated_messages)[0]
            self.stderr.write(
                f"File {pofile}:{line_number} contains untranslated {msgstr} for msgid {repr(msgid)}. [--no-untranslated]"
            )
            exit(1)

        if self.options["check"] and pofile_changed:
            self.stderr.write(f"File {pofile} changed. [--check]")
            if self.verbosity > 1:
                relative_pofile_path = pofile.relative_to(Path.cwd())
                self.stderr.write(
                    "".join(
                        difflib.unified_diff(
                            pofile_content_before_write.splitlines(keepends=True),
                            pofile_content_after_write.splitlines(keepends=True),
                            fromfile=f"a/{relative_pofile_path}",
                            tofile=f"b/{relative_pofile_path}",
                        )
                    )
                )
            exit(1)
