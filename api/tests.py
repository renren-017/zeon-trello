from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

# import tempfile
# from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from boards.models import Project, Board, BoardMember, BoardLastSeen, Column, Card

User = get_user_model()


def get_user(pk):
    return User.objects.get(pk=pk)


def get_image():
    return SimpleUploadedFile(name='test_image.jpg', content=open('media/back_img/pexels-cottonbro-4069291_aqjm4TM.jpg', 'rb').read(),
                              content_type='image/jpeg')


class ProjectTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=User.objects.get(pk=1)).save()

    def test_get_projects(self):
        user = get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-projects'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_project_by_pk(self):
        user = get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_project_post(self):
        data = {
            'title': 'Example 2'
        }
        user = get_user(1)
        self.client.force_login(user)
        response = self.client.post(reverse('api-projects'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], user.pk)
        self.assertEqual(Project.objects.count(), 2)

    def test_project_put(self):
        user = get_user(1)
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
        user = get_user(2)
        self.client.force_login(user)
        response_get = self.client.get(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response_get.status_code, status.HTTP_403_FORBIDDEN)

        data = {
            'title': 'Example Updated'
        }
        response_put = self.client.put(reverse('api-project-detail', kwargs={'pk': 1}), data, format='json',
                                       content_type='application/json')
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_delete(self):
        user = get_user(1)
        self.client.force_login(user)
        response = self.client.delete(reverse('api-project-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


class BoardTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_image()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()

    def test_get_boards(self):
        user = get_user(1)
        self.client.force_login(user)

        response = self.client.get(reverse('api-boards'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_board_create(self):
        user = get_user(1)
        self.client.force_login(user)

        data = {
            'title': 'Example Board',
            'project': 1,
            'background_img': get_image(),
        }
        response = self.client.post(reverse('api-project-boards', kwargs={'pk': 1}), data, format='formdata')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BoardMember.objects.get(board=Board.objects.get(pk=2)).user, get_user(1))
        self.assertEqual(Board.objects.count(), 2)
        self.assertEqual(BoardLastSeen.objects.count(), 1)

    def test_board_get_by_pk(self):
        user = get_user(1)
        user2 = get_user(2)

        self.client.force_login(user)
        response = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')

        self.client.force_login(user2)
        response2 = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')

        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_board_make_and_get_favourite(self):
        self.client.force_login(get_user(1))

        response_make = self.client.get(reverse('api-board-favourite', kwargs={'pk': 1}))
        self.assertEqual(response_make.status_code, status.HTTP_201_CREATED)

        response_get = self.client.get(reverse('api-boards-favourite'), format='json')
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

    def test_board_get_recent(self):
        self.client.force_login(get_user(1))

        response_get = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        response_recent = self.client.get(reverse('api-boards-recent'), format='json')
        self.assertEqual(response_recent.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_recent.data), 1)


#
class ColumnTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_image()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()
        Column(title='Example', board=Board.objects.get(pk=1)).save()

    def test_column_creation(self):
        self.client.force_login(get_user(1))
        data = {'title': 'Example Column'}
        response = self.client.post(reverse('api-columns', kwargs={'pk': 1}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Column.objects.count(), 2)

        self.client.force_login(get_user(2))
        response_unauthorized = self.client.post(reverse('api-columns', kwargs={'pk': 1}), data, format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_column_update(self):
        self.client.force_login(get_user(1))
        data = {'title': 'Example Update'}
        response = self.client.put(reverse('api-column-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client.force_login(get_user(2))
        response_unauthorized = self.client.put(reverse('api-column-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_column_deletion(self):
        self.client.force_login(get_user(2))
        response_unauthorized = self.client.delete(reverse('api-column-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(get_user(1))
        response = self.client.delete(reverse('api-column-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CardTest(TestCase):

    def setUp(self):
        self.user1 = User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        self.user2 = User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_image()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()
        Column(title='Example', board=Board.objects.get(pk=1)).save()
        Card(title='Example', column=Column.objects.get(pk=1), description='bla', deadline=timezone.now()).save()

    def test_card_creation(self):
        self.client.force_login(get_user(1))
        data = {
            'title': 'Example Title',
            'description': 'Some short description',
            'deadline': timezone.now()
        }
        response = self.client.post(reverse('api-cards', kwargs={'pk': 1}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 2)

        self.client.force_login(get_user(2))
        response_unauthorized = self.client.post(reverse('api-cards', kwargs={'pk': 1}), data, format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_update(self):
        self.client.force_login(get_user(1))
        data = {
            'title': 'Example Update',
            'description': 'Some short description',
            'deadline': timezone.now()
        }
        response = self.client.put(reverse('api-card-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

        self.client.force_login(get_user(2))
        response_unauthorized = self.client.put(reverse('api-card-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_deletion(self):
        self.client.force_login(get_user(2))
        response_unauthorized = self.client.delete(reverse('api-card-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Card.objects.count(), 1)

        self.client.force_login(get_user(1))
        response = self.client.delete(reverse('api-card-detail', kwargs={'pk': 1}), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Card.objects.count(), 0)

#
# class CardAssetsTest(TestCase):
#     """ Test module for Column model """
#
#     def setUp(self):
#         board = Board(
#             title='Example Board',
#             background_img=temporary_image()
#         ).save()
#         column = Column(
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
