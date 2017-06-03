from time import time
import discord
from discord.ext import commands


# at least 2 choices, and at most 9 (decimal limitations)
min_size_args = 2
max_size_args = 20

possible_surveys = range(26)


class Survey:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Moderator')
    async def survey(self, ctx):
        """
        Creates an interactive poll for the moderators
            The format to ask a question is :
                               '?survey <question here> ? <survey 1> - <survey 2> - ... ! <nb of minutes for timeout>')
        :param ctx:     The context of the message (cf discord doc)
        """
        message = ctx.message.content.split()[1:]
        # The message of is then deleted, to avoid redundancy
        await self.bot.delete_message(ctx.message)

        query = parse_survey(message)

        # test if the parsing was correct
        if query is None:
            syntax = '?survey <question here> ? <survey 1> - <survey 2> - ... ! nb of minutes for timeout```'
            await self.bot.say('Number of args: minimum : ' + str(min_size_args)
                               + ' args, maximum: ' + str(max_size_args) + '\n'
                               + 'The format to ask a question is : ```xml\n'
                               + syntax)
        else:

            question, args, timeout = query

            # We create the poll's message
            em = discord.Embed(title="{0}'s poll".format(ctx.message.author.name),
                               description=format_surveys(question, args),
                               colour=discord.Colour.blue())

            survey_emojis = convert_surveys(possible_surveys[:len(args):])

            msg = await self.bot.say("", embed=em)
            # we ask the user to wait
            to_delete = await self.bot.say("Please wait until the bot puts all the reactions")

            # We add the possible reactions to help the users
            for emoji in survey_emojis:
                await self.bot.add_reaction(msg, emoji)

            # we delete the waiting message
            await self.bot.delete_message(to_delete)

            # We gather the results
            outputs = []
            total_time = 0
            start = time()
            while total_time < int(timeout):
                res = await self.bot.wait_for_reaction(survey_emojis, message=msg, timeout=abs(timeout - total_time))
                if not failed(res) and res.user != self.bot.user:
                    outputs.append(res)
                end = time()
                total_time += end - start
                start = end

            surveys = [0] * len(args)
            nb_surveys = len(outputs)

            for output in outputs:
                id_survey = survey_results(output.reaction.emoji)
                surveys[id_survey] += 1

            # We show the results
            output = ""
            for i, survey in enumerate(surveys):
                if nb_surveys != 0:
                    percent = round(survey / nb_surveys * 100, 2)
                else:
                    percent = 0
                output += str(i + 1) + ".\t " + l2str(args[i]) + " -> " + str(survey) + " votes. (" + str(
                    percent) + "%)\n"

            em = discord.Embed(title="Results of {0}'s poll".format(ctx.message.author.name),
                               description=output, colour=discord.Colour.dark_green())

            await self.bot.say('', embed=em)


def setup(bot):
    bot.add_cog(Survey(bot))


def parse_survey(message):
    """
    Parses a survey string
        The format is like that:
            question ? survey 1 - survey 2 - survey 3 - more surveys : timeout in minutes
    :param message: the message to parse
    :return:    None if the string is malformed
                (question, args, timeout) is the parse succeded
    """
    # read the question
    question = read_question(message)
    if failed(question):
        return None

    # read the arguments
    args = read_args(message[len(question):])
    if failed(args):
        return None

    # do some checks on the number of args and words
    nb_words = 0
    nb_args = 0
    for arg in args:
        nb_words += len(arg) + 1
        nb_args += 1

    if nb_args < min_size_args or nb_args > max_size_args:
        return None

    # read the timeout
    timeout = int(message[len(question) + nb_words]) * 60

    if failed(timeout):
        return None

    return question, args, timeout


def format_surveys(question, args):
    """
    :param question:    The question the users will have to answer
    :param args:    The possible surveys
    :return:    The string that will be shown for the surveys
    """
    # underlined bold question
    output = "__**" + l2str(question) + "**__\n"

    # Eg: 1. Argument
    #     2. Argument 2
    for i, arg in enumerate(args):
        output += "\t" + chr(ord('A') + i) + ".\t " + l2str(arg) + "\n"

    return output


def convert_surveys(l):
    return [(chr(0x0001f1e6 + x)) for x in l]


def survey_results(char_in):
    return ord(char_in) - 0x0001f1e6


def failed(x):
    """
    :param x: The result of the function call
    :return: True if the result of the function call is None
    """
    return x is None


def l2str(string):
    """
    Nice convert from python str format to human format
    :param string:
    :return:
    """
    return " ".join(str(s) for s in string)


def read_question(string):
    """
    Parses a question
        A question ends with a '?'
        Eg:
            Is my name something ?                      --> is a question
            Lol wtf i can't find what a question is     --> isn't a question
    :param string: The string to parse
    :return:    The question
                (None if failed)
    """
    question = []
    for word in string:
        print(word)
        question.append(word)
        if word is '?':
            return question


def read_args(string):
    """
    Parses arguments
        2 arguments are delimited by the character `-`
        Eg:
            Arg1      Wow it sucks
            Arg2      Heh so nice

            Will look like:
                Wow it sucks - Heh so nice :

    :param string: The string to parse
    :return:    The parsed arguments
                (None if failed)
    """
    args = []
    current = []
    for arg in string:
        if arg is '!':
            if current:
                args.append(current)
            return args

        if arg is "-":
            if current:
                args.append(current)
                current = []
        else:
            current.append(arg + " ")
