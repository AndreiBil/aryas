from src.models import *


async def channel_top_list(count, user: User, server: Server):
    """
    Gets top <count> channels for a user
    :param count: length of top list
    :param user: the user
    :param server: the server
    :return: a SelectQuery with Message.channel with the top channels
    """
    messages = (user.messages
                .select(Message.channel)
                .join(Server, on=(Server.id == Channel.server))
                .switch(Message)
                # peewee needs the ==
                .where(Message.is_command == False,
                       Server.id == server)
                .annotate(Channel)
                .order_by(SQL('count').desc())
                .limit(count))
    return messages


async def user_top_list(count, server: Server):
    """
    Gets top <count> users on the server
    :param count: length of the top list
    :param server: the server
    :return: a SelectQuery with users on the top list
    """
    users = (User
             .select()
             .join(Channel, on=(Channel.id == Message.channel))
             .join(Server, on=(Server.id == Channel.server))
             .switch(User)
             # peewee needs the ==
             .where(Message.is_command == False,
                    User.is_bot == False,
                    Server.id == server)
             .annotate(Message)  # annotate alias to 'count'
             .order_by(SQL('count'))
             .limit(count))
    return users


async def user_total_messages(user: User, server: Server):
    """
    Gets the total amount of messages by the user on the server
    :param user: the user
    :param server: the server
    :return: total count of messages by the user
    """
    total_messages = (user.messages
                      .join(Channel, on=(Channel.id == Message.channel))
                      .join(Server, on=(Server.id == Channel.server))
                      # peewee needs the ==
                      .where(Message.is_command == False,
                             Server.id == server)
                      .count())
    return total_messages

    return total_messages

async def server_total_messages(server: Server):
    """
    Gets the total amount of messages on the server
    :param server: the server
    :return: total count of messages on server
    """
    total_messages = (Message
                      .select()
                      .join(User, on=(User.id == Message.user))
                      .join(Channel, on=(Channel.id == Message.channel))
                      .join(Server, on=(Server.id == Channel.server))
                      # peewee needs the ==
                      .where(Message.is_command == False,
                             User.is_bot == False,
                             Server.id == server)
                      .count())
    return total_messages
