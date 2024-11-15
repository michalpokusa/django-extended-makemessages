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

    @override
    def handle(self, *args, **options):

        if options["extract_all"]:
            self.xgettext_options.append("--extract-all")
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

        super().handle(*args, **options)
