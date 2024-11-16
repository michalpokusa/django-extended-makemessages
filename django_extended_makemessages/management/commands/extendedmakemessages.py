try:
    from typing import override
except ImportError:

    def override(func):
        return func


from argparse import _VersionAction, RawDescriptionHelpFormatter

from django.core.management.base import CommandParser, DjangoHelpFormatter
from django.core.management.commands.makemessages import Command as MakeMessagesCommand

import django_extended_makemessages


class DjangoExtendedMakeMessagesHelpFormatter(
    DjangoHelpFormatter, RawDescriptionHelpFormatter
): ...


class Command(MakeMessagesCommand):

    help = MakeMessagesCommand.help + (
        "\n\n"
        "In addition to the options available in Django's `makemessages` command, this command "
        "exposes selected msgmerge/msguniq/msgattrib/xgettext options that make sense for usage "
        "in a Django project."
    )

    @override
    def create_parser(self, prog_name: str, subcommand: str, **kwargs):
        parser = super().create_parser(prog_name, subcommand, **kwargs)
        parser.formatter_class = DjangoExtendedMakeMessagesHelpFormatter
        return parser

    @override
    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)

        # Replace --version option
        for action in parser._actions:
            if isinstance(action, _VersionAction):
                action.version = django_extended_makemessages.__version__

        # Command specific options
        parser.add_argument(
            "--no-fuzzy-matching",
            action="store_true",
            help="Do not use fuzzy matching when an exact match is not found. This may speed up the operation considerably.",
        )
        parser.add_argument(
            "--extract-all",
            action="store_true",
            help="Extract all strings.",
        )
        parser.add_argument(
            "--keyword",
            nargs="?",
            const=None,
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
            help="Set the output page width. Long strings in the output files will be split across multiple lines in order to ensure that each line’s width (= number of screen columns) is less or equal to the given number.",
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

    @override
    def handle(self, *args, **options):

        # Command specific options
        if options["no_fuzzy_matching"]:
            self.msgmerge_options.append("--no-fuzzy-matching")
        if options["extract_all"]:
            self.xgettext_options.append("--extract-all")
        if options["keyword"] is not None:
            assert isinstance(options["keyword"], list)

            # Remove default keywords
            if None in options["keyword"]:
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

        super().handle(*args, **options)
