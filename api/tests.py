from django.test import TestCase
from rest_framework import status
from django.urls import reverse

import tempfile
from PIL import Image

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
