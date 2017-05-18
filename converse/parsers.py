import apiai
from django.conf import settings
import json


class APIAIParser:
    def __init__(self):
        self.ai = apiai.ApiAI(settings.API_AI_CLIENT_TOKEN)

    def parse(self, text, talk_user):
        request = self.ai.text_request()
        request.session_id = talk_user.session_id
        request.query = text
        response = json.loads(request.getresponse().read())
        params = response["result"]["parameters"]
        contexts = {}
        for context in response["result"]["contexts"]:
            contexts[context["name"]] = context["parameters"]
        return response["result"]["fulfillment"]["speech"], response["result"]["action"],\
            not response["result"]["actionIncomplete"], params, contexts
