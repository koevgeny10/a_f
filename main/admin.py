from django.contrib import admin

from .models import *

admin.site.register(UserLogFail)
admin.site.register(LogHistory)
admin.site.register(LogHistoryType)
admin.site.register(Invitation)

admin.site.register(UserProfile)
admin.site.register(UserSocialNetworks)
admin.site.register(UserFriend)

admin.site.register(Settings)
admin.site.register(Role)
admin.site.register(Club)
admin.site.register(ClubUserLink)
