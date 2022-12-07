from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import time

from django.core.files.uploadedfile import SimpleUploadedFile

from boards.models import Project

User = get_user_model()


def get_user(pk):
    return User.objects.get(pk=pk)


def get_file():
    return SimpleUploadedFile(name='test_image.jpg',
                              content=open('media/back_img/ryan-lum-1ak3Z7ZmtQA-unsplash.jpg', 'rb').read(),
                              content_type='image/jpeg')


class ProjectTest(TestCase):

    def setUp(self):
        User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=User.objects.get(pk=1)).save()

    def test_get_projects(self):
        user = get_user(1)
        self.client.force_login(user)

        start = time.time()
        response = self.client.get(reverse('api-projects'), format='json')
        end = time.time()
        response_time = end-start

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertLess(response_time, 0.02)

    def test_get_project_by_pk(self):
        user = get_user(1)
        self.client.force_login(user)

        start = time.time()
        response = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertLess(end-start, 0.02)

    def test_project_post(self):
        data = {
            'title': 'Example 2'
        }
        user = get_user(1)
        self.client.force_login(user)

        start = time.time()
        response = self.client.post(reverse('api-projects'), data, format='json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], user.pk)
        self.assertEqual(Project.objects.count(), 2)
        self.assertLess(end-start, 0.02)

    def test_project_put(self):
        user = get_user(1)
        data = {
            'title': 'Example Updated'
        }

        self.client.force_login(user)

        start = time.time()
        before = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        after = self.client.put(reverse('api-project-detail', kwargs={'pk': 1}), data, format='json',
                                content_type='application/json')
        end = time.time()

        self.assertEqual(after.status_code, status.HTTP_201_CREATED)
        self.assertEqual(after.data['title'], 'Example Updated')
        self.assertEqual(after.data['owner'], before.data['owner'])
        self.assertLess(end-start, 0.03)

    def test_get_projects_with_failed_authentication(self):
        start = time.time()
        response_get = self.client.get(reverse('api-projects'), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_update_project_with_failed_authentication(self):
        start = time.time()
        response = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_update_project_without_ownership(self):
        user = get_user(2)
        self.client.force_login(user)

        start = time.time()
        response_get = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            'title': 'Example Updated'
        }
        start = time.time()
        response_put = self.client.put(reverse('api-project-detail', kwargs={'pk': 1}), data, format='json',
                                       content_type='application/json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_delete(self):
        user = get_user(1)
        self.client.force_login(user)

        start = time.time()
        response = self.client.delete(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)
