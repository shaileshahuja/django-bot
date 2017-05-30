import abc
import json
import logging

from slackclient import SlackClient

logger = logging.getLogger(__name__)


class QuickReply:
    def __init__(self, text, value=None):
        self.text = text
        self.value = value or text

    def __eq__(self, other):
        return self.text == other.text and self.value == other.value

    def __unicode__(self):
        return "{} - {}".format(self.text, self.value)


class MessengerBase:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def send(self, text):
        """
        Send a text via this messenger
        :param text: string
        :return: bool, true if method is successful
        """
        pass

    def send_text(self, text, quick_replies=None):
        """
        Send a text with a list of actions
        :param text: string
        :param quick_replies: list<action>
        :return: bool, true if method is successful
        """
        pass

    def send_image(self, image_url, quick_replies=None):
        """
        Send an image with a list of actions
        :param image_url: string
        :param quick_replies: list<action>
        :return: bool, true if method is successful
        """
        pass

    def get_latest(self):
        """
        :return: (text, image_url, action_list), of the last message
        """
        pass


class SlackMessenger(MessengerBase):
    def __init__(self, token, channel):
        super(SlackMessenger, self).__init__()
        self.channel = channel
        self.sc = SlackClient(token)

    def send(self, text):
        return self.send_to_slack(text=text)

    def send_image(self, image_url, quick_replies=None):
        attachment = {"fallback": "image", "image_url": image_url, "callback_id": self.channel}
        if quick_replies:
            attachment["actions"] = self.format_quick_replies(quick_replies)
        return self.send_to_slack(attachment=attachment)

    def send_text(self, text, quick_replies=None):
        attachment = {"fallback": "New message", "color": "#3AA3E3", "text": text, "mrkdwn_in": ["text"],
                      "callback_id": self.channel}
        if quick_replies:
            attachment["actions"] = self.format_quick_replies(quick_replies)
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
            action_list = self.parse_quick_replies(attachment)
        return text, image_url, action_list

    @staticmethod
    def parse_quick_replies(attachment):
        if "actions" not in attachment:
            return None
        quick_reply_list = []
        for action_item in attachment["actions"]:
            quick_reply = QuickReply(text=action_item["text"], value=action_item["value"])
            quick_reply_list.append(quick_reply)
        return quick_reply_list

    @staticmethod
    def format_quick_replies(quick_replies):
        quick_reply_list = []
        for quick_reply in quick_replies:
            quick_reply_list.append({
                "name": quick_reply.value,
                "text": quick_reply.text,
                "type": "button",
                "value": quick_reply.value
            })
        return quick_reply_list

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
