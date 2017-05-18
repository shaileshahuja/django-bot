import abc
import logging
import traceback
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class MessengerBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def send_text(self, text, actions=None):
        pass

    def send_image(self, image_url, actions=None):
        pass


class SlackMessenger(MessengerBase):
    def __init__(self, token, channel):
        super(SlackMessenger, self).__init__()
        self.post_url = "https://slack.com/api/chat.postMessage"
        self.token = token
        self.channel = channel

    def send_image(self, image_url, actions=None):
        attachments = '[{"fallback": "image", "image_url":"' + image_url + '", "callback_id": "' + self.channel + \
                      '", "actions": ' + self.format_actions(actions) + '}]'
        return self.send_to_slack(attachments)

    def send_text(self, text, actions=None):
        attachments = '[{"fallback": "New message", "color": "#3AA3E3", "text":"' + text + '","mrkdwn_in": ["text"],' \
                                                                                           ' "callback_id": "' + self.channel + '", "actions": ' + self.format_actions(
            actions) + '}]'
        return self.send_to_slack(attachments)

    @staticmethod
    def format_actions(actions=None):
        action_list = []
        if actions is not None:
            for action in actions:
                action_list.append({
                    "name": action["value"],
                    "text": action["text"],
                    "type": "button",
                    "value": action["value"]
                })
        return str(action_list)

    def send_to_slack(self, attachments):
        slack_params = {"attachments": attachments, "token": self.token, "channel": self.channel, "as_user": True}
        # logger.info(slack_params)
        response = requests.get(self.post_url, params=slack_params)
        # logger.info(str(response.status_code) + ": " + response.content)
        return response

