from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from converse.messengers import SlackMessenger
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from pydoc import locate
from django.conf import settings


class Auth(models.Model):
    @cached_property
    def main_group(self):
        if hasattr(self, "slackauth"):
            return self.slackauth.main_group
        return None

    @property
    def users(self):
        if hasattr(self, "slackauth"):
            return self.slackauth.users
        return None

    @property
    def groups(self):
        if hasattr(self, "slackauth"):
            return self.slackauth.groups
        return None

    @cached_property
    def name(self):
        if hasattr(self, "slackauth"):
            return self.slackauth.name
        return None


class SlackAuth(Auth):
    access_token = models.CharField(max_length=200)
    team_id = models.CharField(max_length=30, unique=True)
    team_name = models.CharField(max_length=200)
    bot_id = models.CharField(max_length=30)
    bot_access_token = models.CharField(max_length=200)

    @cached_property
    def main_group(self):
        return self.slack_channels.filter(is_main=True).first()

    @property
    def users(self):
        return self.slack_users

    @property
    def groups(self):
        return self.slack_channels

    @cached_property
    def name(self):
        return self.team_name

    def __unicode__(self):
        return self.team_name


class Group(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def auth(self):
        if hasattr(self, "slackchannel"):
            return self.slackchannel.auth
        return None

    @cached_property
    def messenger(self):
        if hasattr(self, "slackchannel"):
            return self.slackchannel.messenger
        return None

    @cached_property
    def session_id(self):
        if hasattr(self, "slackchannel"):
            return self.slackchannel.session_id
        return None

    @property
    def members(self):
        """Returns a set of TalkUsers"""
        if hasattr(self, "slackchannel"):
            return self.slackchannel.members
        return None

    def __unicode__(self):
        return self.name


class SlackChannel(Group):
    slack_auth = models.ForeignKey(to=SlackAuth, related_name='slack_channels')
    slack_id = models.CharField(max_length=30)
    is_main = models.BooleanField(default=False)

    @property
    def auth(self):
        return self.slack_auth

    @cached_property
    def messenger(self):
        return SlackMessenger(self.slack_auth.bot_access_token, self.slack_id)

    @cached_property
    def session_id(self):
        return self.slack_auth.team_id + "-" + self.slack_id

    @property
    def members(self):
        if self.is_main:
            return self.slack_auth.slack_users.all()
        return None

    class Meta:
        unique_together = ('slack_id', 'slack_auth')


class AbstractUserQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        converse_user = kwargs.pop("converse_user", None)
        if converse_user is not None:
            kwargs["content_type_id"] = ContentType.objects.get_for_model(converse_user).pk
            kwargs["object_id"] = converse_user.id
        return super(AbstractUserQuerySet, self).get(*args, **kwargs)


class AbstractUser(models.Model):
    objects = AbstractUserQuerySet.as_manager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    _converse_user = GenericForeignKey('content_type', 'object_id')

    @property
    def converse_user(self):
        """
        :return: ConverseUser instance
        """
        assert isinstance(self._converse_user, TalkUser)
        return self._converse_user

    @property
    def messenger(self):
        return self._converse_user.messenger

    @property
    def name(self):
        return self._converse_user.name

    @property
    def email(self):
        return self._converse_user.email

    @property
    def natural_identifier(self):
        return self._converse_user.natural_identifier

    @property
    def auth(self):
        return self._converse_user.auth

    class Meta:
        abstract = True


@receiver(post_save, dispatch_uid="create app users")
def create_app_user(sender, instance, created, **kwargs):
    if isinstance(instance, TalkUser) and created:
        AppUser = locate(settings.DJANGO_BOT_USER)
        assert issubclass(AppUser, AbstractUser)
        AppUser.objects.create(_converse_user=instance)


class TalkUser(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def natural_identifier(self):
        return self.email if not self.name else self.name

    @property
    def auth(self):
        if hasattr(self, "slackuser"):
            return self.slackuser.auth
        return None

    @cached_property
    def messenger(self):
        """Returns conversation of the application with the user"""
        if hasattr(self, "slackuser"):
            return self.slackuser.messenger
        return None

    @cached_property
    def session_id(self):
        if hasattr(self, "slackuser"):
            return self.slackuser.session_id
        return None

    def __unicode__(self):
        return self.natural_identifier

    # class Meta:
    #     abstract = True


class SlackUser(TalkUser):
    slack_id = models.CharField(max_length=30)
    slack_channel = models.CharField(max_length=30, null=True, blank=True)
    slack_auth = models.ForeignKey(to=SlackAuth, related_name='slack_users')

    @property
    def auth(self):
        return self.slack_auth

    @cached_property
    def messenger(self):
        return SlackMessenger(self.slack_auth.bot_access_token, self.slack_channel or self.slack_id)

    @cached_property
    def session_id(self):
        return self.slack_auth.team_id + "-" + self.slack_id

    class Meta:
        unique_together = ('slack_id', 'slack_auth')
