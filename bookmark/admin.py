from django.contrib import admin

from bookmark.models import CustomUser, Bookmarks, Follow, Tags

# Register your models here.



admin.site.register(CustomUser)
admin.site.register(Bookmarks)
admin.site.register(Follow)
admin.site.register(Tags)
