from discord.ext.commands.formatter import HelpFormatter, Paginator
from discord.ext.commands import Command
import inspect
import itertools


class AryasFormatter(HelpFormatter):
    def __init__(self):
        super().__init__()
        self._paginator = Paginator()

    def format(self):
        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)
        print(description)
        return ['test']

        # # we need a padding of ~80 or so
        #
        # description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)
        #
        # if description:
        #     # <description> portion
        #     self._paginator.add_line(description, empty=True)
        #
        # if isinstance(self.command, Command):
        #     # <signature portion>
        #     signature = self.get_command_signature()
        #     self._paginator.add_line(signature, empty=True)
        #
        #     # <long doc> section
        #     if self.command.help:
        #         self._paginator.add_line(self.command.help, empty=True)
        #
        #     # end it here if it's just a regular command
        #     if not self.has_subcommands():
        #         self._paginator.close_page()
        #         return self._paginator.pages
        #
        # max_width = self.max_name_size
        #
        # def category(tup):
        #     cog = tup[1].cog_name
        #     # we insert the zero width space there to give it approximate
        #     # last place sorting position.
        #     return cog + ':' if cog is not None else '\u200bNo Category:'
        #
        # if self.is_bot():
        #     data = sorted(self.filter_command_list(), key=category)
        #     for category, commands in itertools.groupby(data, key=category):
        #         # there simply is no prettier way of doing this.
        #         commands = list(commands)
        #         if len(commands) > 0:
        #             self._paginator.add_line(category)
        #
        #         self._add_subcommands_to_page(max_width, commands)
        # else:
        #     self._paginator.add_line('Commands:')
        #     self._add_subcommands_to_page(max_width, self.filter_command_list())
        #
        # # add the ending note
        # self._paginator.add_line()
        # ending_note = self.get_ending_note()
        # self._paginator.add_line(ending_note)
        # return self._paginator.pages
