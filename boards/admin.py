from django.contrib import admin
from .models import *


class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'background_img', 'is_starred', 'is_active', 'created_on', 'last_modified')
    list_filter = ('is_starred', 'is_active')
    search_fields = ('members', 'title')


class BarAdmin(admin.ModelAdmin):
    list_display = ('title', 'board')
    list_filter = ('board',)
    search_fields = ('title',)


class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'bar', 'description', 'deadline')
    list_filter = ('bar',)
    search_fields = ('title',)


admin.site.register(Board, BoardAdmin)
admin.site.register(Bar, BarAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(CardChecklistItem)
admin.site.register(CardFile)
admin.site.register(CardComment)
admin.site.register(CardLabel)
