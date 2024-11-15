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

        if options["sort_output"]:
            self.msgmerge_options.append("--sort-output")
        if options["sort_by_file"]:
            self.msgmerge_options.append("--sort-by-file")

        super().handle(*args, **options)
