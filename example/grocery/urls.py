from django.conf.urls import url
from views import SlackOAuthSuccessView, SlackOAuthFailureView

urlpatterns = [
    url(r'^success', SlackOAuthSuccessView.as_view(), name='success'),
    url(r'^failure', SlackOAuthFailureView.as_view(), name='failure')
]
