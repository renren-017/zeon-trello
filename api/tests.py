from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

import tempfile
from PIL import Image

from boards.models import Project, Board

User = get_user_model()


def temporary_image():
    image = Image.new("RGB", (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file, 'jpeg')
    tmp_file.seek(0)
    return tmp_file


class ProjectTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=User.objects.get(pk=1)).save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_get_projects(self):
        user = self.get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-projects'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_by_pk(self):
        user = self.get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_project_post(self):
        data = {
            'title': 'Example 2'
        }
        user = self.get_user(1)
        self.client.force_login(user)
        response = self.client.post(reverse('api-projects'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], user.pk)
        self.assertEqual(Project.objects.count(), 2)

    def test_project_put(self):
        user = self.get_user(1)
        data = {
            'title': 'Example Updated'
        }

        self.client.force_login(user)
        before = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        after = self.client.put(reverse('api-project-detail', kwargs={'pk': 1}), data, format='json',
                                content_type='application/json')

        self.assertEqual(after.status_code, status.HTTP_201_CREATED)
        self.assertEqual(after.data['title'], 'Example Updated')
        self.assertNotEqual(after.data['title'], before.data['title'])
        self.assertEqual(after.data['owner'], before.data['owner'])

    def test_get_projects_with_failed_authentication(self):
        response_get = self.client.get(reverse('api-projects'), format='json')
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_update_project_with_failed_authentication(self):
        response = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_update_project_without_ownership(self):
        user = self.get_user(2)
        self.client.force_login(user)
        response_get = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            'title': 'Example Updated'
        }
        response_put = self.client.put(reverse('api-project-detail', kwargs={'pk': 1}), data, format='json',
                                       content_type='application/json')
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)


class BoardTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=User.objects.get(pk=1)).save()

    def get_user(self, pk):
        return User.objects.get(pk=pk)

    def test_get_boards(self):
        user = self.get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-boards'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # def test_board_create(self):
    #     user = self.get_user(1)
    #     self.client.force_login(user)
    #
    #     data = {
    #         'title': 'Example Board',
    #         'project': 1,
    #         'background_img': temporary_image(),
    #     }
    #     response = self.client.post(reverse('api-boards'), data, format='formdata')
    #
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data), 1)

#
# class BarTest(TestCase):
#     """ Test module for Column model """
#
#     def setUp(self):
#         Board(
#             title='Example Board',
#             background_img=temporary_image()
#         ).save()
#
#     def test_bar_creation(self):
#         data = {
#             'board': 1,
#             'title': 'Example Column',
#         }
#         response = self.client.post(reverse('bars'), data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#
# class CardTest(TestCase):
#     """ Test module for Column model """
#
#     def setUp(self):
#         board = Board(
#             title='Example Board',
#             background_img=temporary_image()
#         ).save()
#         bar = Column(
#             board=board,
#             title='Example Column'
#         ).save()
#
#     def test_card_creation(self):
#         data = {
#             'bar': 1,
#             'title': 'Example Card',
#             'description': 'Some short description',
#             'deadline': datetime.now()
#         }
#         response = self.client.post(reverse('cards'), data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#
# class CardAssetsTest(TestCase):
#     """ Test module for Column model """
#
#     def setUp(self):
#         board = Board(
#             title='Example Board',
#             background_img=temporary_image()
#         ).save()
#         bar = Column(
#             board=board,
#             title='Example Column'
#         ).save()
#         card = Card(
#             bar=bar,
#             title='Example Card',
#             description='Some description',
#             deadline=datetime.now()
#         ).save()
#
#     def test_card_label_creation(self):
#         data = {
#             'card': 1,
#             'title': 'Example Label',
#             'color': '#e2e2e2',
#         }
#         response = self.client.post(reverse('cards'), data, format='json')
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
