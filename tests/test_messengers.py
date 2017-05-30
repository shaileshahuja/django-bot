import unittest
import os

from converse.messengers import SlackMessenger, MessengerBase, QuickReply


class TestMessenger(unittest.TestCase):
    def setUp(self):
        self.messengers = {"slack": SlackMessenger(os.environ["SLACK_TOKEN"], os.environ["SLACK_CHANNEL"])}
        self.actions = [QuickReply("1"), QuickReply(text="2", value="2")]

    def test_send(self):
        text = "hello"
        for api, messenger in self.messengers.items():
            assert isinstance(messenger, MessengerBase)
            res = messenger.send(text)
            self.assertTrue(res)
            res_text, _, _ = messenger.get_latest()
            self.assertEqual(text, res_text)

    def test_send_text(self):
        text = "hello"
        for api, messenger in self.messengers.items():
            assert isinstance(messenger, MessengerBase)
            response = messenger.send_text(text, self.actions)
            self.assertTrue(response)
            res_text, _, res_actions = messenger.get_latest()
            self.assertEqual(text, res_text)
            self.assertEqual(len(self.actions), len(res_actions))
            for one, two in zip(self.actions, res_actions):
                self.assertEqual(one, two)

    def test_send_image(self):
        image_url = "http://www.planwallpaper.com/static/cache/00/b7/00b7a21d94164cb8764457a894063606.jpg"
        for api, messenger in self.messengers.items():
            assert isinstance(messenger, MessengerBase)
            response = messenger.send_image(image_url, self.actions)
            self.assertTrue(response)
            _, res_image_url, res_actions = messenger.get_latest()
            self.assertEqual(image_url, res_image_url)
            self.assertEqual(len(self.actions), len(res_actions))
            for one, two in zip(self.actions, res_actions):
                self.assertEqual(one, two)
