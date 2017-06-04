# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic.base import TemplateView


class SlackOAuthSuccessView(TemplateView):
    template_name = "success.html"


class SlackOAuthFailureView(TemplateView):
    template_name = "failure.html"
