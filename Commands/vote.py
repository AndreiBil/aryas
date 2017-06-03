from time import time

import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(vote_module(bot))


# at least 2 choices, and at most 9 (decimal limitations)
min_size_args = 2
max_size_args = 9

# reactions that can be used for the votes
possible_votes = [
    "\u0031\u20e3",  # 1
    "\u0032\u20e3",  # 2
    "\u0033\u20e3",  # 3
    "\u0034\u20e3",  # 4
    "\u0035\u20e3",  # 5
    "\u0036\u20e3",  # 6
    "\u0037\u20e3",  # 7
    "\u0038\u20e3",  # 8
    "\u0039\u20e3",  # 9
]

vote_results = {
    "\u0031\u20e3": 0,
    "\u0032\u20e3": 1,
    "\u0033\u20e3": 2,
    "\u0034\u20e3": 3,
    "\u0035\u20e3": 4,
    "\u0036\u20e3": 5,
    "\u0037\u20e3": 6,
    "\u0038\u20e3": 7,
    "\u0039\u20e3": 8,
}


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


def parse_vote(message):
    """
    Parses a vote string
        The format is like that:
            question ? vote 1 - vote 2 - vote 3 - more votes : timeout in seconds
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
    timeout = float(message[len(question) + nb_words])

    if failed(timeout):
        return None

    return question, args, timeout


def format_votes(question, args):
    """
    :param question:    The question the users will have to answer
    :param args:    The possible votes
    :return:    The string that will be shown for the votes
    """
    # underlined bold question
    output = "__**" + l2str(question) + " ?**__\n"

    # Eg: 1. Argument
    #     2. Argument 2
    for i, arg in enumerate(args):
        output += "\t" + str(i + 1) + ".\t " + l2str(arg) + "\n"

    return output


class vote_module:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.has_role('Moderator')
    async def vote(self, ctx):
        """
        Creates an interactive poll for the moderators
            The format to ask a question is :
                               '?vote <question here> ? <vote 1> - <vote 2> - ... ! <nb of seconds for timeout>')
        :param ctx:     The context of the message (cf discord doc)
        """
        message = ctx.message.content.split()[1:]
        # The message of is then deleted, to avoid redundancy
        await self.bot.delete_message(ctx.message)

        query = parse_vote(message)

        # test if the parsing was correct
        if query is None:
            await self.bot.say('Error in parsing.\n'
                               'Number of args: minimum : 2 args, maximum: 9\n'
                               'The format to ask a question is : ```xml\n'
                               '?vote <question here> ? <vote 1> - <vote 2> - ... ! nb of seconds for timeout```')
        else:

            question, args, timeout = query

            # We create the poll's message
            em = discord.Embed(title="{0}'s poll".format(ctx.message.author.name),
                               description=format_votes(question, args),
                               colour=discord.Colour.blue())

            vote_emojis = possible_votes[:len(args):]

            msg = await self.bot.say("", embed=em)
            # we ask the user to wait
            to_delete = await self.bot.say("Please wait until the bot puts all the reactions")

            # We add the possible reactions to help the users
            for emoji in vote_emojis:
                await self.bot.add_reaction(msg, emoji)

            # we delete the waiting message
            await self.bot.delete_message(to_delete)

            # We gather the results
            outputs = []
            total_time = 0
            start = time()
            while total_time < timeout:
                res = await self.bot.wait_for_reaction(vote_emojis, message=msg, timeout=abs(timeout - total_time))
                if not failed(res) and res.user != self.bot.user:
                    outputs.append(res)
                end = time()
                total_time += end - start
                start = end

            votes = [0] * len(args)
            nb_votes = len(outputs)

            for output in outputs:
                id_vote = vote_results[output.reaction.emoji]
                votes[id_vote] += 1


            # We show the results
            output = ""
            for i, vote in enumerate(votes):
                if nb_votes != 0:
                    percent = round(vote / nb_votes * 100, 2)
                else:
                    percent = 0
                output += str(i + 1) + ".\t " + l2str(args[i]) + " -> " + str(vote) + " votes. (" + str(percent) + "%)\n"

            em = discord.Embed(title="Results of {0}'s poll".format(ctx.message.author.name),
                               description=output, colour=discord.Colour.dark_green())

            await self.bot.say('', embed=em)
