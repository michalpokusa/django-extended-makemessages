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

    @override
    def handle(self, *args, **options):
        super().handle(*args, **options)
