import discord
from discord.ext import commands
from discord.ext.commands import bot as bot_module
from src.formatter import AryasFormatter

description = 'An in development python bot for the discord platform'
bot_prefix = '?'
bot = commands.Bot(command_prefix=bot_prefix, description=description, pm_help=True, formatter=AryasFormatter())
bot.remove_command('help')


@bot.command(pass_context=True, name='help', hidden=True)
async def aryas_help(ctx, *commands):
    """Shows this message."""
    # Adapted from discord.ext.commands.bot._default_help_command.
    # The only thing that has been changed is the last send command
    # which now sends embeds instead of normal text messages
    bot = ctx.bot
    destination = ctx.message.author if bot.pm_help else ctx.message.channel

    def repl(obj):
        return bot_module._mentions_transforms.get(obj.group(0), '')

    # help by itself just lists our own commands.
    if len(commands) == 0:
        pages = bot.formatter.format_help_for(ctx, bot)
    elif len(commands) == 1:
        # try to see if it is a cog name
        name = bot_module._mention_pattern.sub(repl, commands[0])
        if name in bot.cogs:
            command = bot.cogs[name]
        else:
            command = bot.commands.get(name)
            if command is None:
                await bot.send_message(destination, bot.command_not_found.format(name))
                return

        pages = bot.formatter.format_help_for(ctx, command)
    else:
        name = bot_module._mention_pattern.sub(repl, commands[0])
        command = bot.commands.get(name)
        if command is None:
            await bot.send_message(destination, bot.command_not_found.format(name))
            return

        for key in commands[1:]:
            try:
                key = bot_module._mention_pattern.sub(repl, key)
                command = command.commands.get(key)
                if command is None:
                    await bot.send_message(destination, bot.command_not_found.format(key))
                    return
            except AttributeError:
                await bot.send_message(destination, bot.command_has_no_subcommands.format(command, key))
                return

        pages = bot.formatter.format_help_for(ctx, command)
    for embed in pages:
        # This has been changed to send embeds
        await bot.send_message(destination, embed=embed)

# TODO: Build startup_extensions dynamically
# Config and AryasORM must be loaded first
startup_extensions = ['config', 'aryasorm', 'general', 'modtools', 'fun', 'statistics']


@bot.event
async def on_ready():
    print('Logged in')
    print('Name : {}'.format(bot.user.name))
    print('ID : {}'.format(bot.user.id))
    print(discord.__version__)


def main():
    for extension in startup_extensions:
        extension = 'src.extensions.' + extension
        try:
            bot.load_extension(extension)
        except Exception as e:
            raise e

    config = bot.cogs['Config']
    bot.run(config['discord']['token'])
