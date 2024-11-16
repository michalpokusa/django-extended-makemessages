try:
    from typing import override
except ImportError:

    def override(func):
        return func

from django.core.management.commands.makemessages import Command as MakeMessagesCommand


class Command(MakeMessagesCommand):

    @override
    def add_arguments(self, parser: CommandParser):
        super().add_arguments(parser)
        parser.add_argument(
            "--extract-all",
            action="store_true",
            help="Extract all strings.",
        )
        parser.add_argument(
            "--keyword",
            action="append",
            help="Specify keywordspec as an additional keyword to be looked for. Without a keywordspec, the option means to not use default keywords.",
        )
        parser.add_argument(
            "--force-po",
            action="store_true",
            help="Always write an output file even if no message is defined.",
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
        parser.add_argument(
            "--no-fuzzy-matching",
            action="store_true",
            help="Do not use fuzzy matching when an exact match is not found. This may speed up the operation considerably.",
        )

    @override
    def handle(self, *args, **options):

        if options["extract_all"]:
            self.xgettext_options.append("--extract-all")
        if options["keyword"]:
            self.xgettext_options += [
                f"--keyword={keywordspec}" for keywordspec in options["keyword"]
            ]
        if options["force_po"]:
            self.xgettext_options.append("--force-po")

        if options["sort_output"]:
            self.msgmerge_options.append("--sort-output")
        if options["sort_by_file"]:
            self.msgmerge_options.append("--sort-by-file")

        if options["indent"]:
            self.xgettext_options.append("--indent")
            self.msgmerge_options.append("--indent")
            self.msgattrib_options.append("--indent")
        if options["width"]:
            self.xgettext_options.append(f"--width={options['width']}")
            self.msgmerge_options.append(f"--width={options['width']}")
            self.msgattrib_options.append(f"--width={options['width']}")

        if options["no_fuzzy_matching"]:
            self.msgmerge_options.append("--no-fuzzy-matching")

        super().handle(*args, **options)
