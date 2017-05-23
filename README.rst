django-bot
===================
A django library that makes it easier to develop bots with a common interface for messaging platforms (eg. Slack, FB messenger) and natural langauge parsers (eg. api.ai).

|build-status| |pypi-version|

.. |build-status| image:: https://travis-ci.org/shaileshahuja/django-bot.svg?branch=develop
    :target: https://travis-ci.org/shaileshahuja/django-bot
.. |pypi-version| image:: https://badge.fury.io/py/django-bot.svg
    :target: https://pypi.python.org/pypi/django-bot

Overview
===================
BETA version: Currently django-bot only supports Slack and api.ai. Future plans include supporting more messaging platforms (Facebook Messenger, Telegram, Kik, Google assistant, Cortana, Skype, Alexa), and more natural langauge parsers (AWS, wit.ai).

This library helps to maintain authenticated users and groups in the database and allows you to respond to any messages as well as initiate conversations with any of those.

Requirements and Installation
******************************

django-bot for Python works with Python 2.7, 3.4, 3.5, 3.6 and django >= 1.8, and requires ``PyPI`` to install dependencies. The message parsing and delivery is done in the background with the help of celery. It also requires slackclient and apiai python libraries for communication with the external services. 

.. code-block:: bash

	pip install django-bot

Of course, if you prefer doing things the hard way, by pulling down the source code directly into your project:

.. code-block:: bash

	git clone https://github.com/shaileshahuja/django-bot.git

Basic classes
==================== 
``converse.messengers.MessengerBase``
*************************************** 
This class provides the API for all messenger classes. ``converse.messengers.SlackMessenger`` implements this API, and so will all future implementations of other messengers.

Methods:
^^^^^^^^^^
``send``: To send a plaintext message.

``send_text``: To send a message with actions.

``send_image``: To send an image with actions.

Actions are instant prompts for the user to click and respond. In Slack, they are sent as quick replies. 

``converse.parsers.APIAIParser``
*************************************** 
Parsers implement the parse method, which receives the text to be parsed and the session id.

Getting started
====================
The following steps will help you get started with django-bot.

``settings.py``

.. code-block:: python

   SLACK_CLIENT_ID = '<your slack client id>'
   SLACK_CLIENT_SECRET = '<your slack client secret>'
   SLACK_VERIFICATION_TOKEN = '<your slack verification token>'

   # right now this is the only supported NLP framework for chatbots
   TEXT_PARSER = 'converse.parsers.APIAIParser'
   API_AI_CLIENT_TOKEN = '<your api.ai client token>'
   
   # when actions are returned from the NLP framework, they need to be parsed and executed
   # ClassNameExecutor will call execute method in CLASS_EXECUTOR_PREFIX + camelCase(action) + CLASS_EXECUTOR_SUFFIX
   # for the following settings, if action is passed as 'portfolio.buy', an instance of myapp.actions.PortfolioBuyQuery
   # will be constructed with arguments (talk_user, params, contexts) and the execute method will be called
   ACTION_EXECUTOR = 'converse.executors.ClassNameExecutor'
   CLASS_EXECUTOR_PREFIX = 'myapp.actions.'
   CLASS_EXECUTOR_SUFFIX = 'Query'

``urls.py``

.. code-block:: python

   urlpatterns = [
       ...,
       url(r'^converse/', include('converse.urls', namespace='converse'))
   ]

``models.py``

.. code-block:: python

   from django.db import models
   from django.db.models.signals import post_save
   from django.dispatch.dispatcher import receiver
   from converse.models import TalkUser, AbstractUser
   
   @receiver(post_save, dispatch_uid="create my app users")
   def create_tickerbot_user(sender, instance, created, **kwargs):
       if isinstance(instance, TalkUser) and created:
           MyUser.objects.create(talk_user=instance)

   class MyUser(AbstractUser):
       my_field = models.BooleanField(default=True)
