import unittest
import os

from converse.messengers import SlackMessenger, MessengerBase


class TestMessenger(unittest.TestCase):
    def setUp(self):
        self.messengers = {"slack": SlackMessenger(os.environ["SLACK_TOKEN"], os.environ["SLACK_CHANNEL"])}

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
        actions = [{"text": "1", "value": "1"}, {"text": "2", "value": "2"}]
        for api, messenger in self.messengers.items():
            assert isinstance(messenger, MessengerBase)
            response = messenger.send_text(text, actions)
            self.assertTrue(response)
            res_text, _, res_actions = messenger.get_latest()
            self.assertEqual(text, res_text)
            self.assertEqual(len(actions), len(res_actions))
            for one, two in zip(actions, res_actions):
                self.assertEqual(one, two)

    def test_send_image(self):
        image_url = "http://www.planwallpaper.com/static/cache/00/b7/00b7a21d94164cb8764457a894063606.jpg"
        actions = [{"text": "1", "value": "1"}, {"text": "2", "value": "2"}]
        for api, messenger in self.messengers.items():
            assert isinstance(messenger, MessengerBase)
            response = messenger.send_image(image_url, actions)
            self.assertTrue(response)
            _, res_image_url, res_actions = messenger.get_latest()
            self.assertEqual(image_url, res_image_url)
            self.assertEqual(len(actions), len(res_actions))
            for one, two in zip(actions, res_actions):
                self.assertEqual(one, two)
