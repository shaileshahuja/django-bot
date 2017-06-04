from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.functional import cached_property
from converse.messengers import SlackMessenger
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
import logging
logger = logging.getLogger(__name__)


class Auth(models.Model):
    @cached_property
    def messenger(self):
        if hasattr(self, "slackauth"):
            return self.slackauth.messenger
        return None

    @property
    def users(self):
        converse_users = self._users
        AppUser = AbstractUser.implementation()
        return AppUser.objects.filter(content_type_id=ContentType.objects.get_for_model(converse_users.first()).pk,
                                      object_id__in=[converse_user.pk for converse_user in converse_users.all()])

    @property
    def _users(self):
        if hasattr(self, "slackauth"):
            return self.slackauth._users
        return []

    # @property
    # def groups(self):
    #     if hasattr(self, "slackauth"):
    #         return self.slackauth.groups
    #     return None

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
    def messenger(self):
        queryset = self.slack_channels.filter(is_main=True)
        if queryset.exists():
            return queryset.first().messenger
        return None

    @property
    def _users(self):
        return self.slack_users

    # @property
    # def groups(self):
    #     return self.slack_channels

    @cached_property
    def name(self):
        return self.team_name

    def __unicode__(self):
        return self.team_name


class Group(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def org(self):
        return AbstractOrganization.implementation().objects.get(converse_org=self._org)

    @property
    def _org(self):
        if hasattr(self, "slackchannel"):
            return self.slackchannel._org
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

    # @property
    # def members(self):
    #     """Returns a set of TalkUsers"""
    #     if hasattr(self, "slackchannel"):
    #         return self.slackchannel.members
    #     return None

    def __unicode__(self):
        return self.name


class SlackChannel(Group):
    slack_auth = models.ForeignKey(to=SlackAuth, related_name='slack_channels')
    slack_id = models.CharField(max_length=30)
    is_main = models.BooleanField(default=False)

    @property
    def _org(self):
        return self.slack_auth

    @cached_property
    def messenger(self):
        return SlackMessenger(self.slack_auth.bot_access_token, self.slack_id)

    @cached_property
    def session_id(self):
        return self.slack_auth.team_id + "-" + self.slack_id

    # @property
    # def members(self):
    #     return None

    class Meta:
        unique_together = ('slack_id', 'slack_auth')


class TalkUser(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def natural_identifier(self):
        return self.email if not self.name else self.name

    @property
    def org(self):
        return AbstractOrganization.implementation().objects.get(converse_org=self._org)

    @property
    def _org(self):
        if hasattr(self, "slackuser"):
            return self.slackuser._org
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
    def _org(self):
        return self.slack_auth

    @cached_property
    def messenger(self):
        return SlackMessenger(self.slack_auth.bot_access_token, self.slack_channel or self.slack_id)

    @cached_property
    def session_id(self):
        return self.slack_auth.team_id + "-" + self.slack_id

    class Meta:
        unique_together = ('slack_id', 'slack_auth')


class AbstractUserQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        converse_user = kwargs.pop("converse_user", None)
        if converse_user is not None:
            kwargs["content_type_id"] = ContentType.objects.get_for_model(converse_user).pk
            kwargs["object_id"] = converse_user.pk
        return super(AbstractUserQuerySet, self).get(*args, **kwargs)


class AbstractUser(models.Model):
    objects = AbstractUserQuerySet.as_manager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    _converse_user = GenericForeignKey('content_type', 'object_id')

    def __getattr__(self, item):
        if not item.startswith('_'):
            try:
                return getattr(self._converse_user, item)
            except AttributeError:
                pass
        raise AttributeError("'{}' object has no attribute '{}'".format(type(self), item))

    @classmethod
    def implementation(cls):
        sub = cls.__subclasses__()
        if len(sub) != 1:
            error = "{} should have exactly 1 subclass, current subclasses: {} ".format(cls, sub)
            logger.error(error)
            raise RuntimeError(error)
        return sub[0]

    def __unicode__(self):
        return self._converse_user.natural_identifier

    class Meta:
        abstract = True


class AbstractOrganizationQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        converse_org = kwargs.pop("converse_org", None)
        if converse_org is not None:
            kwargs["content_type_id"] = ContentType.objects.get_for_model(converse_org).pk
            kwargs["object_id"] = converse_org.pk
        return super(AbstractOrganizationQuerySet, self).get(*args, **kwargs)


class AbstractOrganization(models.Model):
    objects = AbstractOrganizationQuerySet.as_manager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    _converse_org = GenericForeignKey('content_type', 'object_id')

    def __getattr__(self, item):
        if not item.startswith('_'):
            try:
                return getattr(self._converse_org, item)
            except AttributeError:
                pass
        raise AttributeError("'{}' object has no attribute '{}'".format(type(self), item))

    @classmethod
    def implementation(cls):
        sub = cls.__subclasses__()
        if len(sub) != 1:
            error = "{} should have exactly 1 subclass, current subclasses: {} ".format(cls, sub)
            logger.error(error)
            raise RuntimeError(error)
        return sub[0]

    def __unicode__(self):
        return self._converse_org.name

    class Meta:
        abstract = True


@receiver(post_save, dispatch_uid="create app users")
def create_app_models(sender, instance, created, **kwargs):
    if isinstance(instance, TalkUser) and created:
        AbstractUser.implementation().objects.create(_converse_user=instance)
    if isinstance(instance, Auth) and created:
        AbstractOrganization.implementation().objects.create(_converse_org=instance)
