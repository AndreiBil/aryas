from discord.ext.commands.formatter import HelpFormatter
from discord.ext.commands import Command
from discord.ext.commands import Group
import discord
import datetime
import inspect
import itertools


class AryasPaginator:
    """
    A class that helps with paginating Discord embedded messages

    Attributes
    -----------
    title: str
        The title of all discord embeds.
    description: str
        The description of all discord embeds.
    footer: str
        The footer of all discord embeds
    """
    def __init__(self, title='', description='', footer=''):
        self._max_fields = 25
        self._max_field_length = 1024
        self._title = title
        self._description = description
        self._footer = footer
        self._field_name = ''
        self._char_count = 0
        self._count = 0
        self._current_page: discord.Embed = None
        self._line_buffer = []
        self._pages = []

    def add_line(self, line):
        """
        Appends lines to the line buffer
        :param line: the line to append
        """
        self._char_count += len(line)

        # if the field gets to large we can't send it to discord
        # TODO: come up with a way to split the field nicely
        if self._char_count >= self._max_field_length:
            raise RuntimeError('Too many characters in field')
        self._line_buffer.append(line)

    def set_name(self, name):
        """
        Set the current field name
        :param name: name of the field (required)
        """
        self._field_name = name

    def new_page(self, title='', description='', timestamp=True):
        """
        Creates a new page and resets the count
        :param title: title of new page
        :param description: description of new page
        :param timestamp: boolean for including timestamp
        """
        if self._current_page is not None:
            self._pages.append(self._current_page)
        if timestamp:
            self._current_page = discord.Embed(title=title, description=description, timestamp=datetime.datetime.now())
        else:
            self._current_page = discord.Embed(title=title, description=description)
        self._current_page.set_footer(text=self._footer)
        self._count = 0

    def make_field(self, inline=True):
        """
        Creates and adds the embed field to the page.

        Uses the current field name and line buffer
        :param inline: boolean for if the field is inline or not
        """
        if self._field_name == '':
            raise RuntimeError('name is a required field')
        if self._current_page is None or self._count >= self._max_fields:
            self.new_page(title=self._title, description=self._description)
        self._current_page.add_field(name=self._field_name, value='\n'.join(self._line_buffer), inline=inline)
        self._field_name = ''
        self._line_buffer = []
        self._char_count = 0
        self._count += 1

    def close_page(self):
        """
        Closes the current page
        """
        if self._current_page:
            self._pages.append(self._current_page)
            self._current_page = None
            self._count = 0

    @property
    def pages(self):
        """
        Returns the embeds
        :return: a list of discord.Embed
        """
        if self._count > 0:
            self.close_page()
        return self._pages


class AryasFormatter(HelpFormatter):
    """
    Formats the help command. Adapted from discord.ext.commands.formatter.HelpFormatter
    """
    def __init__(self):
        super().__init__()

    def _add_entries(self, commands):
        """
        Adds commands from a dict to the paginator
        :param commands: the dict with commands
        """
        for name, command in commands:
            # skip aliases
            if name in command.aliases:
                continue

            if isinstance(command, Group):
                self._expand_group(command, '')
                continue

            entry = '{0} - {1}'.format(name, command.short_doc)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)
    
    def _expand_group(self, group, prefix):
        """
        Recursively expands a Group into paginator
        :param group: the Group to expand
        :param prefix: prefix of the line
        """
        if not isinstance(group, Group):
            entry = '{prefix}{0} - {1}'.format(group.name, group.short_doc, prefix=prefix)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)
        else:
            entry = '{prefix}{0} - {1}'.format(group.name, group.short_doc, prefix=prefix)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)
            for subcommand in group.commands.copy().values():
                # Build the prefix with group name so we get a nice list
                self._expand_group(subcommand, '    {prefix}{0} '.format(group.name, prefix=prefix))

    def format(self):
        """
        Formats the help page.
        """
        # Adapted from discord.ext.commands.formatter.HelpFormatter.format

        self._paginator = AryasPaginator()

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            self._paginator.new_page(description=description)

        if isinstance(self.command, Command):
            # long help doc
            if self.command.help:
                self._paginator.add_line(self.command.help)

            self._paginator.set_name(self.get_command_signature())
            self._paginator.make_field(inline=False)

            # if it's just a single command we're done here
            if not self.has_subcommands():
                return self._paginator.pages

        # Helper method for sorting by category (cog)
        def category(tup):
            cog = tup[1].cog_name
            # Unicode invisible space is there to set No Category last
            return cog + ':' if cog is not None else '\u200bNo Category:'

        # if command is a bot we need to process the entire command list
        if self.is_bot():
            data = sorted(self.filter_command_list(), key=category)
            for category, commands in itertools.groupby(data, key=category):
                commands = list(commands)
                if len(commands) > 0:
                    self._add_entries(commands)
                    self._paginator.set_name(category)
                    self._paginator.make_field(inline=False)
        else:
            # if command is just a cog or Group we can print all the commands
            # returned by filter_command_list
            self._add_entries(self.filter_command_list())
            self._paginator.set_name('Commands:')
            self._paginator.make_field(inline=False)

        # Get the ending message
        self._paginator.set_name('More:')
        self._paginator.add_line(self.get_ending_note())
        self._paginator.make_field(inline=False)
        return self._paginator.pages
