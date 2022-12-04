import sys

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='projects')


class Board(models.Model):
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name='boards')
    title = models.CharField(max_length=50)
    background_img = models.ImageField(upload_to='back_img/')
    is_archived = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BoardMember(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='boards')

    def __str__(self):
        return f'{self.board.id}:{self.user.id}'


class BoardLastSeen(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='last_seen_boards')
    timestamp = models.DateTimeField(auto_now=True)


class BoardFavourite(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='favourite_boards')


class Column(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE, related_name='bars')
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Card(models.Model):
    bar = models.ForeignKey(to=Column, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    deadline = models.DateTimeField()
    checklist = models.JSONField()

    def __str__(self):
        return self.title


class CardComment(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=300)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body


class CardFile(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='card_files/')

    def __str__(self):
        return self.file


class Mark(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE, related_name='marks')
    title = models.CharField(max_length=30)
    color = models.CharField(default='#000', max_length=7)

    def __str__(self):
        return self.title


class CardMark(models.Model):
    mark = models.ForeignKey(to=Mark, on_delete=models.CASCADE)
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='marks')

    def __str__(self):
        return self.mark
