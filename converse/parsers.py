import abc
import json
import apiai
from django.conf import settings


class ParserResponse:
    def __init__(self):
        # response text to be sent to the user instantly
        self.text = None

        # any action to be executed via the Executor.execute method
        self.action = None

        # a boolean to indicate whether slot filling is complete for the current text
        # Action is executed if and only if this is True
        self.slot_filling_complete = False

        # dict (str: str) of parameters parsed from the text
        self.params = {}

        # a dict (str: dict), the outer dict has keys as the name of the contexts
        # the inner dict has key-value pairs for params in these contexts
        self.contexts = {}

    def __unicode__(self):
        return "Text: {}, Action: {}, Params: {}, Contexts: {}".format(self.text, self.action, self.params,
                                                                       self.contexts)


class ParserBase:
    __metaclass__ = abc.ABCMeta

    def parse(self, query, session_id):
        """
        Parses the given text, and uses the session id to remember the conversation history (for context)
        :param text: String
        :param session_id: String
        :return: ParserResponse
        """
        pass


class APIAIParser(ParserBase):
    def __init__(self):
        self.ai = apiai.ApiAI(settings.API_AI_CLIENT_TOKEN)

    def parse(self, query, session_id):
        request = self.ai.text_request()
        request.session_id = session_id
        request.query = query
        response = json.loads(request.getresponse().read().decode())
        contexts = {}
        for context in response["result"]["contexts"]:
            contexts[context["name"]] = context["parameters"]
        parser_response = ParserResponse()
        parser_response.text = response["result"]["fulfillment"]["speech"]
        parser_response.action = response["result"]["action"]
        parser_response.params = response["result"]["parameters"]
        parser_response.contexts = contexts
        parser_response.slot_filling_complete = not response["result"]["actionIncomplete"]
        return parser_response
