import json
import logging
import traceback

from django.conf import settings
from django.http.response import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic.base import View
from slackclient import SlackClient

from converse.models import SlackAuth
from converse.tasks import retrieve_channel_users
from converse.tasks import slack_message_event, slack_action_event

logger = logging.getLogger(__name__)


def get_slack_oauth_uri(request):
    scope = "bot"
    return "https://slack.com/oauth/authorize?scope=" + scope + "&client_id=" + settings.SLACK_CLIENT_ID + \
           "&redirect_uri=" + request.build_absolute_uri(reverse("converse:slack:oauth"))


class SlackOAuthView(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            code = request.GET.get('code', '')
            sc = SlackClient("")
            result = sc.api_call("oauth.access", client_id=settings.SLACK_CLIENT_ID,
                                 client_secret=settings.SLACK_CLIENT_SECRET, code=code,
                                 redirect_uri=request.build_absolute_uri(reverse('converse:slack:oauth')))
            if not result["ok"]:
                raise RuntimeError(result["error"])
            queryset = SlackAuth.objects.filter(team_id=result["team_id"])
            if queryset.exists():
                queryset.update(access_token=result["access_token"], team_name=result["team_name"],
                                bot_id=result["bot"]["bot_user_id"], bot_access_token=result["bot"]["bot_access_token"])
                slack_auth = queryset.get()
            else:
                slack_auth = SlackAuth.objects.create(access_token=result["access_token"], team_id=result["team_id"],
                                                      team_name=result["team_name"],
                                                      bot_id=result["bot"]["bot_user_id"],
                                                      bot_access_token=result["bot"]["bot_access_token"])
            retrieve_channel_users.delay(slack_auth.pk)
            return HttpResponseRedirect(reverse(settings.SLACK_OAUTH_SUCCESS_VIEW))
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponseRedirect(reverse(settings.SLACK_OAUTH_FAILURE_VIEW))


class SlackActionView(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            query = request.POST
            logger.debug(str(query))
        except Exception:
            logger.error(traceback.format_exc())
        return HttpResponse(status=200)


class SlackActionURL(View):
    def post(self, request):
        try:
            query = json.loads(request.POST["payload"])
            logger.debug(str(query))
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponse(status=400)
        if settings.SLACK_VERIFICATION_TOKEN != query["token"]:
            return HttpResponse(status=400)
        slack_action_event.delay(query)
        return HttpResponse(status=200)


class SlackRequestURL(View):
    def post(self, request):
        try:
            query = json.loads(request.body)
            logger.debug(str(query))
        except Exception:
            logger.error(traceback.format_exc())
            return HttpResponse(status=400)
        if settings.SLACK_VERIFICATION_TOKEN != query["token"]:
            return HttpResponse(status=400)
        if query["type"] == "url_verification":
            return HttpResponse(status=200, content=query["challenge"])
        if query["type"] == "event_callback":
            event = query["event"]
            if event["type"] == "message" and "bot_id" not in event:
                slack_message_event.delay(query["team_id"], event)
        return HttpResponse(status=200)
