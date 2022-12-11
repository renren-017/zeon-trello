from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import time

from django.core.files.uploadedfile import SimpleUploadedFile

from boards.models import Project, Board, BoardMember, Column

User = get_user_model()


def get_user(pk):
    return User.objects.get(pk=pk)


def get_file():
    return SimpleUploadedFile(name='test_image.jpg',
                              content=open('media/back_img/ryan-lum-1ak3Z7ZmtQA-unsplash.jpg', 'rb').read(),
                              content_type='image/jpeg')


class ColumnTest(TestCase):

    def setUp(self):
        User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_file()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()
        Column(title='Example', board=Board.objects.get(pk=1)).save()

    def test_column_creation(self):
        self.client.force_login(get_user(1))
        data = {'title': 'Example Column'}
        start = time.time()
        response = self.client.post(reverse('api-columns', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Column.objects.count(), 2)

        self.client.force_login(get_user(2))
        start = time.time()
        response_unauthorized = self.client.post(reverse('api-columns', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertLess(end-start, 0.05)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_column_update(self):
        self.client.force_login(get_user(1))
        data = {'title': 'Example Update'}
        start = time.time()
        response = self.client.put(reverse('api-column-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_login(get_user(2))
        start = time.time()
        response_unauthorized = self.client.put(reverse('api-column-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        end = time.time()

        self.assertLess(end-start, 0.025)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_column_deletion_with_and_without_proper_permissions(self):
        self.client.force_login(get_user(2))
        start = time.time()
        response_unauthorized = self.client.delete(reverse('api-column-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.025)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(get_user(1))
        start = time.time()
        response = self.client.delete(reverse('api-column-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.025)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)