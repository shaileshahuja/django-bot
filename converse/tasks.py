import logging
from pydoc import locate

from celery.app import shared_task
from django.conf import settings
from slackclient import SlackClient

from converse.executors import Executor
from converse.models import TalkUser, SlackAuth, SlackUser, SlackChannel, AbstractUser
from converse.parsers import ParserResponse

logger = logging.getLogger(__name__)
parser_class = locate(settings.TEXT_PARSER)


@shared_task
def slack_message_event(team_id, event):
    slack_auth = SlackAuth.objects.get(team_id=team_id)
    slack_user_id = event["user"]
    try:
        slack_user = SlackUser.objects.get(slack_auth=slack_auth, slack_id=slack_user_id)
    except SlackUser.DoesNotExist:
        sc = SlackClient(slack_auth.bot_access_token)
        result = sc.api_call("users.info", user=slack_user_id)
        slack_user = SlackUser.objects.create(name=result["user"]["profile"]["real_name"],
                                              email=result["user"]["profile"]["email"],
                                              slack_auth=slack_auth, slack_id=slack_user_id)
    message_event(slack_user, event["text"])


@shared_task
def slack_action_event(action_event):
    slack_auth = SlackAuth.objects.get(team_id=action_event["team"]["id"])
    slack_user_id = action_event["user"]["id"]
    try:
        slack_user = SlackUser.objects.get(slack_auth=slack_auth, slack_id=slack_user_id)
    except SlackUser.DoesNotExist:
        sc = SlackClient(slack_auth.bot_access_token)
        result = sc.api_call("users.info", user=slack_user_id)
        if not result["ok"]:
            logger.error("Unable to call 'users.info' for user id: {} with slack auth: {}".format(slack_user_id,
                                                                                                  slack_auth))
            return
        user_channel = get_user_channel_map(sc, slack_auth)
        user = result["user"]
        if user_channel is not None and user["id"] in user_channel:
            slack_channel = user_channel[user["id"]]
        else:
            logger.warn("Unable to find channel ID for user id: {} with slack auth: {}".format(user["id"], slack_auth))
            slack_channel = None
        slack_user = SlackUser.objects.create(email=user["profile"]["email"], name=user["profile"]["real_name"],
                                              slack_id=user["id"], slack_channel=slack_channel, slack_auth=slack_auth)
    message_event(slack_user, action_event["actions"][0]["value"])


def message_event(converse_user, message):
    assert isinstance(converse_user, TalkUser)
    parser = parser_class()
    response = parser.parse(message, converse_user.session_id)
    assert isinstance(response, ParserResponse)
    logger.debug(response)
    if response.text:
        converse_user.messenger.send(response.text)
    if response.slot_filling_complete and response.action:
        app_user = AbstractUser.implementation().objects.get(converse_user=converse_user)
        Executor.execute(action=response.action, user=app_user, params=response.params, contexts=response.contexts)


@shared_task
def update_user_list():
    for slack_auth in SlackAuth.objects.all():
        retrieve_channel_users(slack_auth.pk)


@shared_task
def retrieve_channel_users(slack_auth_id):
    slack_auth = SlackAuth.objects.get(pk=slack_auth_id)
    sc = SlackClient(slack_auth.bot_access_token)
    channels = sc.api_call("channels.list")
    if not channels["ok"]:
        return
    for channel in channels["channels"]:
        if not SlackChannel.objects.filter(slack_id=channel['id'], slack_auth=slack_auth).exists():
            SlackChannel.objects.create(slack_auth=slack_auth, slack_id=channel['id'],
                                        is_main=channel["is_general"], name=channel['name'])
    users = sc.api_call("users.list")
    if not users["ok"]:
        return
    user_channel = get_user_channel_map(sc, slack_auth)
    if user_channel is None:
        return
    for user in users["members"]:
        if user["is_bot"] or user["id"] == "USLACKBOT" or user["id"] not in user_channel:
            continue
        if SlackUser.objects.filter(slack_id=user["id"], slack_auth=slack_auth).exists():
            SlackUser.objects.filter(slack_id=user["id"],
                                     slack_auth=slack_auth).update(email=user["profile"]["email"],
                                                                   name=user["profile"]["real_name"],
                                                                   slack_channel=user_channel[user["id"]])
        else:
            SlackUser.objects.create(email=user["profile"]["email"], name=user["profile"]["real_name"],
                                     slack_id=user["id"], slack_channel=user_channel[user["id"]],
                                     slack_auth=slack_auth)


def get_user_channel_map(sc, slack_auth):
    dms = sc.api_call("im.list")
    if not dms["ok"]:
        logger.error("Unable to call im.list for {}".format(slack_auth))
        return None
    user_channel = {}
    for dm in dms["ims"]:
        user_channel[dm["user"]] = dm["id"]
    return user_channel
