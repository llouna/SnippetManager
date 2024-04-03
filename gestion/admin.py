from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Snippet, Tag, User, GroupTags


admin.site.register(Snippet)
admin.site.register(Tag)
admin.site.register(User, UserAdmin)
admin.site.register(GroupTags)

