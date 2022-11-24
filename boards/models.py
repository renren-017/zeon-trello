from django.db import models
from django.contrib.auth import get_user_model
from colorfield.fields import ColorField

User = get_user_model()


class Board(models.Model):
    title = models.CharField(max_length=50)
    background_img = models.ImageField(upload_to='back_img/')
    is_starred = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(to=User, related_name='boards')


class Bar(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE, related_name='bars')
    title = models.CharField(max_length=30)


class Card(models.Model):
    bar = models.ForeignKey(to=Bar, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    deadline = models.DateTimeField()


class CardComment(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=300)
    created_on = models.DateTimeField(auto_now_add=True)


class CardFile(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='card_files/')


class CardLabel(models.Model):
    # + def Board.tags
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='labels')
    title = models.CharField(max_length=30)
    color = ColorField(default='#000')


class CardCheckList(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=30)


class CardChecklistItem(models.Model):
    checklist = models.ForeignKey(to=CardCheckList, on_delete=models.CASCADE, related_name='items')
    content = models.TextField(max_length=300)
    is_done = models.BooleanField(default=False)
