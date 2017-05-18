from django.conf.urls import url, include

from converse.views import SlackRequestURL, SlackOAuthView, SlackActionURL

slackpatterns = [
    url(r'^oauth', SlackOAuthView.as_view(), name='oauth'),
    url(r'^webhook', SlackRequestURL.as_view(), name='webhook'),
    url(r'^action', SlackActionURL.as_view(), name='action')
]

urlpatterns = [
    url(r'^slack/', include(slackpatterns, namespace='slack'))
]
