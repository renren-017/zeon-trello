from django.contrib import admin
from .models import *


class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'project','title', 'background_img', 'created_on', 'last_modified')
    search_fields = ('title',)


class BarAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board')
    list_filter = ('board',)
    search_fields = ('title',)


class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'column', 'description', 'deadline')
    list_filter = ('column',)
    search_fields = ('title',)


admin.site.register(Board, BoardAdmin)
admin.site.register(Column, BarAdmin)
admin.site.register(BoardMember)
admin.site.register(BoardFavourite)
admin.site.register(BoardLastSeen)
admin.site.register(Card, CardAdmin)
admin.site.register(CardFile)
admin.site.register(CardMark)
admin.site.register(CardComment)
admin.site.register(Mark)
