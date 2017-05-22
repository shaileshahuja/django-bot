import abc
import json
import logging

from slackclient import SlackClient

logger = logging.getLogger(__name__)


class MessengerBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def send(self, text):
        pass

    def send_text(self, text, actions=None):
        pass

    def send_image(self, image_url, actions=None):
        pass

    def get_latest(self):
        pass


class SlackMessenger(MessengerBase):
    def __init__(self, token, channel):
        super(SlackMessenger, self).__init__()
        self.channel = channel
        self.sc = SlackClient(token)

    def send(self, text):
        return self.send_to_slack(text=text)

    def send_image(self, image_url, actions=None):
        attachment = {"fallback": "image", "image_url": image_url, "callback_id": self.channel}
        if actions:
            attachment["actions"] = self.format_actions(actions)
        return self.send_to_slack(attachment=attachment)

    def send_text(self, text, actions=None):
        attachment = {"fallback": "New message", "color": "#3AA3E3", "text": text, "mrkdwn_in": ["text"],
                      "callback_id": self.channel}
        if actions:
            attachment["actions"] = self.format_actions(actions)
        return self.send_to_slack(attachment=attachment)

    def get_latest(self):
        message = self.sc.api_call("im.history", count=1, channel=self.channel)["messages"][0]
        text = message["text"]
        image_url = None
        action_list = None
        if "attachments" in message:
            attachment = message["attachments"][0]
            if "image_url" in attachment:
                image_url = attachment["image_url"]
            if "text" in attachment:
                text = attachment["text"]
            action_list = self.parse_actions(attachment)
        return text, image_url, action_list

    def parse_actions(self, attachment):
        if "actions" not in attachment:
            return None
        action_list = []
        for action_item in attachment["actions"]:
            action = {"text": action_item["text"], "value": action_item["value"]}
            action_list.append(action)
        return action_list

    @staticmethod
    def format_actions(actions):
        action_list = []
        for action in actions:
            action_list.append({
                "name": action["value"],
                "text": action["text"],
                "type": "button",
                "value": action["value"]
            })
        return action_list

    def send_to_slack(self, text=None, attachment=None):
        params = {"channel": self.channel, "as_user": True, "mrkdwn": True}
        if attachment:
            params["attachments"] = json.dumps([attachment])
        if text:
            params["text"] = text
        response = self.sc.api_call("chat.postMessage", **params)
        # logger.info(params)
        if not response["ok"]:
            logger.debug(response)
        return response["ok"]
