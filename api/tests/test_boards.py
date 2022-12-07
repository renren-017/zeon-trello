from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import time

from django.core.files.uploadedfile import SimpleUploadedFile

from boards.models import Project, Board, BoardMember, BoardLastSeen

User = get_user_model()


def get_user(pk):
    return User.objects.get(pk=pk)


def get_file():
    return SimpleUploadedFile(name='test_image.jpg',
                              content=open('media/back_img/ryan-lum-1ak3Z7ZmtQA-unsplash.jpg', 'rb').read(),
                              content_type='image/jpeg')


class BoardTest(TestCase):

    def setUp(self):
        User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        User(email='n3@user.com', password='foo', first_name='N3', last_name='U3').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_file()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()

    def test_get_boards(self):
        user = get_user(1)
        self.client.force_login(user)

        start = time.time()
        response = self.client.get(reverse('api-boards'), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_board_create(self):
        user = get_user(1)
        self.client.force_login(user)

        data = {
            'title': 'Example Board',
            'project': 1,
            'background_img': get_file(),
        }

        start = time.time()
        response = self.client.post(reverse('api-project-boards', kwargs={'pk': 1}), data, format='formdata')
        end = time.time()

        self.assertLess(end-start, 0.3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BoardMember.objects.get(board=Board.objects.get(pk=2)).user, get_user(1))
        self.assertEqual(Board.objects.count(), 2)
        self.assertEqual(BoardLastSeen.objects.count(), 1)

    def test_board_get_by_pk(self):
        user = get_user(1)
        user2 = get_user(2)

        self.client.force_login(user)
        start = time.time()
        response = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_login(user2)
        start = time.time()
        response2 = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_member_to_board(self):
        self.client.force_login(get_user(1))
        data = {
            'user': 'n2@user.com'
        }

        start = time.time()
        response = self.client.post(reverse('api-board-add-member', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(BoardMember.objects.filter(board=Board.objects.get(pk=1), user=get_user(2)).exists())
        self.assertLess(end-start, 0.03)

        self.client.force_login(get_user(2))
        data = {
            'user': 'n3@user.com'
        }
        start = time.time()
        response_unauthorized = self.client.post(reverse('api-board-add-member', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(end-start, 0.02)

    def test_board_make_and_get_favourite(self):
        self.client.force_login(get_user(1))
        data = {
            'board': 1
        }

        start = time.time()
        response_make = self.client.post(reverse('api-boards-favourite'), data, format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_make.status_code, status.HTTP_201_CREATED)

        start = time.time()
        response_get = self.client.get(reverse('api-boards-favourite'), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

    def test_board_get_recent(self):
        self.client.force_login(get_user(1))

        start = time.time()
        response_get = self.client.get(reverse('api-board-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)

        start = time.time()
        response_recent = self.client.get(reverse('api-boards-recent'), format='json')
        end = time.time()

        self.assertLess(end-start, 0.02)
        self.assertEqual(response_recent.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_recent.data), 1)
