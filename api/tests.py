from django.test import TestCase
from rest_framework import status
from django.urls import reverse

import tempfile
from PIL import Image
from datetime import datetime

from boards.models import Board, Bar, Card


def temporary_image():
    image = Image.new("RGB", (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file, 'jpeg')
    tmp_file.seek(0)
    return tmp_file


class BoardTest(TestCase):
    """ Test module for Board model """

    def test_board_creation(self):
        data = {
            'title': 'Example Board',
            'background_img': temporary_image(),
        }
        response = self.client.post(reverse('boards'), data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BarTest(TestCase):
    """ Test module for Bar model """

    def setUp(self):
        Board(
            title='Example Board',
            background_img=temporary_image()
        ).save()

    def test_bar_creation(self):
        data = {
            'board': 1,
            'title': 'Example Bar',
        }
        response = self.client.post(reverse('bars'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CardTest(TestCase):
    """ Test module for Bar model """

    def setUp(self):
        board = Board(
            title='Example Board',
            background_img=temporary_image()
        ).save()
        bar = Bar(
            board=board,
            title='Example Bar'
        ).save()

    def test_card_creation(self):
        data = {
            'bar': 1,
            'title': 'Example Card',
            'description': 'Some short description',
            'deadline': datetime.now()
        }
        response = self.client.post(reverse('cards'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CardAssetsTest(TestCase):
    """ Test module for Bar model """

    def setUp(self):
        board = Board(
            title='Example Board',
            background_img=temporary_image()
        ).save()
        bar = Bar(
            board=board,
            title='Example Bar'
        ).save()
        card = Card(
            bar=bar,
            title='Example Card',
            description='Some description',
            deadline=datetime.now()
        ).save()

    def test_card_label_creation(self):
        data = {
            'card': 1,
            'title': 'Example Label',
            'color': '#e2e2e2',
        }
        response = self.client.post(reverse('cards'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
