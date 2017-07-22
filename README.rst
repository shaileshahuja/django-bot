django-bot
==========
A django library that makes it easier to develop bots with a common interface for messaging platforms (eg. Slack, FB messenger) and natural language parsers (eg. api.ai).

.. image:: https://travis-ci.org/shaileshahuja/django-bot.svg?branch=develop
    :target: https://travis-ci.org/shaileshahuja/django-bot
.. image:: https://badge.fury.io/py/django-bot.svg
    :target: https://pypi.python.org/pypi/django-bot

Overview
========
BETA version: Currently django-bot only supports Slack and api.ai. Future plans include supporting more messaging platforms (Facebook Messenger, Telegram, Kik, Google assistant, Cortana, Skype, Alexa), and more natural language parsers (AWS Lex, wit.ai).

This library helps to maintain authenticated users and groups in the database and allows you to respond to any messages as well as initiate conversations with any of those.

Requirements and Installation
*****************************

django-bot for Python works with Python 2.7, 3.4, 3.5, 3.6 and django >= 1.8, and requires ``PyPI`` to install dependencies. The message parsing and delivery is done in the background with the help of celery. It also requires slackclient and apiai python libraries for communication with the external services. 

.. code-block:: bash

    pip install django-bot

Of course, if you prefer doing things the hard way, by pulling down the source code directly into your project:

.. code-block:: bash

    git clone https://github.com/shaileshahuja/django-bot.git

Add to ``INSTALLED_APPS``

``settings.py``

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'converse',
       # your apps
   ]

   # must remove CSRFMiddleware
   MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
   ]

   # making sure reversing URLs produces https instead of http, required for Slack integration
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

Getting started
===============

User model
**********

First, we need to define the model and attributes of every user communicating with the bot.

``models.py``

.. code-block:: python

   from converse.models import AbstractUser

   class MyUser(AbstractUser):
       credits = models.FloatField(default=0.0)

This user model is automatically created for each authenticated user. For example, if a slack team is authenticated, ``MyUser`` object will be created for each user in the team. Make sure to define defaults for all fields.

Default properties available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``org``: The organization this user belongs to.

``messenger``: Returns an implementation of ``converse.messengers.MessengerBase`` object. This messenger object can be used to send messages to the user. It exposes a consistent interface for different platforms.

``email``: The email address of the user, if available

``name``: The name of the user, if available

Organization model
******************

You must also define a model that will be instantiated for each organization that authenticates your bot. Again, remember to define defaults for any custom fields.

``models.py``

.. code-block:: python

   from converse.models import AbstractOrganization

   class Organization(AbstractOrganization):
       pass

Default properties available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``users``: A queryset of user objects that belong to this organization

``messenger``: Returns an implementation of ``converse.messengers.MessengerBase`` object. This messenger object can be used to send messages to a group common to all members of the organization. In Slack, if your bot is added, this can send a message to #general,

``name``: The name of the organization, if available

Sending messages as the bot
***************************

By using ``user.messenger`` or ``org.messenger``, you can get access to an implementation of ``converse.messengers.MessengerBase``, such as ``converse.messengers.SlackMessenger``.

Methods:
^^^^^^^^
``send``: To send a plaintext message.

``send_text``: To send a message with quick replies.

``send_image``: To send an image with quick replies.

Quick replies are instant prompts for the user to click and respond. In Slack, they are sent as actions.

Example:

.. code-block:: python

   user.messenger.send_text("Are you sure?", quick_replies=[QuickReply("yes"), QuickReply(text="Cancel", value="No")])

Clicking on 'yes' will send a request back to your server with query ``QuickReply.value``.

Parsers
*******

Parsers are responsible for understanding the intent of the user from the text query, which receives the text to be parsed and the session id. The session id can be used to respond to queries with context.
``converse.parsers.APIAIParser`` is one such parser that connects to api.ai.

Integrating with api.ai
^^^^^^^^^^^^^^^^^^^^^^^

``settings.py``

.. code-block:: python

   # right now this is the only supported NLP framework for chatbots
   TEXT_PARSER = 'converse.parsers.APIAIParser'
   API_AI_CLIENT_TOKEN = '<your api.ai client token>'

To match the actions in api.ai to the actions you write, make sure the name in ``@Executor(action="<name>")`` is the same as the one the 'actions' field in your intent. You can access the slot filling params using ``self.params`` and the conversation context using ``self.contexts``.

Implementing your own parser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't wish to use api.ai, you can implement your own parser.

``parsers.py``

.. code-block:: python

   from converse.parsers import ParserBase, ParserResponse

   class MyParser(ParserBase):
       def parse(self, query, session_id):
           # your code
           ...
           response = ParserResponse()
           response.text = ... # this will be sent instantly to the user
           response.action = ... # this action will be called, if slot filling is complete
           response.slot_filling_complete = ... # determines whether the query is complete
           response.params = ... # parameters extracted from 'query'
           response.contexts = ... # context of this conversation

           return response

Have a look at the ``ParserResponse`` class for more information.

Actions
*******

Actions define a unit of execution that is called in the background using celery. These can be triggered when the user sends a message. The natural language parser will detect the intent of the user, extract parameters and the pass action be to taken back to the calling program. An action should be decorated with ``Executor``, which defines the name of the corresponding action. The decorated object can either be a subclass of ``ActionBase`` and implement the ``execute`` method, or a method can receives user, params and contexts as kwargs.

``actions.py``

.. code-block:: python

   from converse.executors import Executor, ActionBase
   from converse.messengers import QuickReply

   @Executor(action="account.balance")
   class CreditsAction(ActionBase):
       def execute(self):
           self.user.messenger.send("Please wait while we retrieve your details...")
           # this method is called in the background, so it is safe to make time consuming API requests
           account_type = self.contexts["accounts"]["type"]
           date_from = self.params["date_from"]

           self.user.messenger.send_text("You have ${:.2f} left in your {} account".format(self.user.credits, account_type),
                                         quick_replies=[QuickReply("buy credits"), QuickReply("redeem gift")])

We also need to tell django where the action classes / methods are written.

``settings.py``

.. code-block:: python

   ACTION_MODULES = ['<list of modules where actions can be found>'] # ['x.actions']

Integrating with Slack
**********************
Copy the credentials from the developer portal to your django application. If this is your first time with a Slack application, please read the documentation from Slack on getting started. You have to give bot permission, create a bot user and subscribe to bot events.

``settings.py``

.. code-block:: python

   SLACK_CLIENT_ID = '<your slack client id>'
   SLACK_CLIENT_SECRET = '<your slack client secret>'
   SLACK_VERIFICATION_TOKEN = '<your slack verification token>'

   # django-bot will redirect the users to reverse(value) when oauth is successful or fails
   SLACK_OAUTH_SUCCESS_VIEW = '<django success url name>' # grocery:success
   SLACK_OAUTH_FAILURE_VIEW = '<django failure url name>' # grocery:failure

Next, add this to your django URLs.

``urls.py``

.. code-block:: python

   urlpatterns = [
       ...,
       url(r'^converse/', include('converse.urls', namespace='converse'))
   ]

Next, start your server (behind https, try ngrok if in development environment), and add these URLs to your Slack app.

OAuth & Permissions -> Redirect URLs: <https base url>/converse/slack/oauth

Event Subscriptions -> Request URL: <https base url>/converse/slack/webhook

Interactive Messages -> Request URL: <https base url>/converse/slack/action

After these steps, when someone authenticates a Slack team, the Organization and User objects will be created in an async task.

