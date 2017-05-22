from django.contrib import admin

from converse.models import SlackUser, SlackChannel, SlackAuth, Auth, TalkUser, Group

admin.site.register(Auth)
admin.site.register(SlackAuth)
admin.site.register(TalkUser)
admin.site.register(SlackUser)
admin.site.register(Group)
admin.site.register(SlackChannel)
