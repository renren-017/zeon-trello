import sys

from django.db import models
from django.contrib.auth import get_user_model
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

User = get_user_model()


class Board(models.Model):
    title = models.CharField(max_length=50)
    background_img = models.ImageField(upload_to='back_img/')
    is_starred = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(to=User, related_name='boards')

    def __str__(self):
        return self.title

    def save(self):
        # Opening the uploaded image
        im = Image.open(self.background_img)
        output = BytesIO()

        # Resize/modify the image
        im = im.convert('RGB')
        im = im.resize((100, 100))

        # after modifications, save it to the output
        im.save(output, format='JPEG', quality=80)
        output.seek(0)

        # change the imagefield value to be the newly modified image value
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.background_img.name.split('.')[0], 'image/jpeg',
                                          sys.getsizeof(output), None)

        super(Board, self).save()


class Bar(models.Model):
    board = models.ForeignKey(to=Board, on_delete=models.CASCADE, related_name='bars')
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Card(models.Model):
    bar = models.ForeignKey(to=Bar, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500)
    deadline = models.DateTimeField()

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


class CardLabel(models.Model):
    # + def Board.tags
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='labels')
    title = models.CharField(max_length=30)
    color = models.CharField(default='#000', max_length=7)

    def __str__(self):
        return self.title


class CardChecklistItem(models.Model):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE, related_name='checklist_items')
    content = models.TextField(max_length=300)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.content