from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
import time

from django.core.files.uploadedfile import SimpleUploadedFile

from boards.models import Project, Board, BoardMember, Column, Card, Mark, CardMark

User = get_user_model()

optimal_response_time = 0.03

def get_user(pk):
    return User.objects.get(pk=pk)


def get_file():
    return SimpleUploadedFile(name='test_image.jpg',
                              content=open('media/back_img/ryan-lum-1ak3Z7ZmtQA-unsplash.jpg', 'rb').read(),
                              content_type='image/jpeg')


class CardTest(TestCase):

    def setUp(self):
        User(email='n@user.com', password='foo', first_name='N', last_name='U').save()
        User(email='n2@user.com', password='foo', first_name='N2', last_name='U2').save()
        Project(title='Example', owner=get_user(1)).save()
        Board(title='Example', project=Project.objects.get(pk=1), background_img=get_file()).save()
        BoardMember(user=get_user(1), board=Board.objects.get(pk=1)).save()
        Column(title='Example', board=Board.objects.get(pk=1)).save()
        Card(title='Example', column=Column.objects.get(pk=1), description='bla', deadline=timezone.now()).save()
        Mark(board=Board.objects.get(pk=1), title='Important', color='#fff').save()
        CardMark(card=Card.objects.get(pk=1), mark=Mark.objects.get(pk=1)).save()

    def test_card_creation(self):
        self.client.force_login(get_user(1))
        data = {
            'title': 'Example Title',
            'description': 'Some short description',
            'deadline': timezone.now()
        }
        start = time.time()
        response = self.client.post(reverse('api-cards', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertLess(end-start, optimal_response_time)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 2)

    def test_card_creation_without_proper_permissions(self):
        self.client.force_login(get_user(2))
        data = {
            'title': 'Example Title',
            'description': 'Some short description',
            'deadline': timezone.now()
        }
        start = time.time()
        response_unauthorized = self.client.post(reverse('api-cards', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertLess(end-start, optimal_response_time)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_update(self):
        self.client.force_login(get_user(1))
        data = {
            'title': 'Example Update',
            'description': 'Some short description',
            'checklist': {
                'to-do': False
            },
            'deadline': timezone.now()
        }
        start = time.time()
        response = self.client.put(reverse('api-card-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        end = time.time()

        self.assertLess(end-start, 0.05)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 1)

        self.client.force_login(get_user(2))
        start = time.time()
        response_unauthorized = self.client.put(reverse('api-card-detail', kwargs={'pk': 1}), data, format='json', content_type='application/json')
        end = time.time()

        self.assertLess(end-start, optimal_response_time)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)

    def test_card_deletion(self):
        self.client.force_login(get_user(2))
        start = time.time()
        response_unauthorized = self.client.delete(reverse('api-card-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, optimal_response_time)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Card.objects.count(), 1)

        self.client.force_login(get_user(1))
        start = time.time()
        response = self.client.delete(reverse('api-card-detail', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertLess(end-start, optimal_response_time)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Card.objects.count(), 0)

    def test_get_board_marks(self):
        self.client.force_login(get_user(1))

        start = time.time()
        response_board = self.client.get(reverse('api-board-mark', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertEqual(response_board.status_code, status.HTTP_200_OK)
        self.assertLess(end-start, optimal_response_time)

    def test_get_board_marks_unauthorized(self):
        self.client.force_login(get_user(2))

        start = time.time()
        response_board = self.client.get(reverse('api-board-mark', kwargs={'pk': 1}), format='json')
        end = time.time()

        self.assertEqual(response_board.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_card_marks(self):
        self.client.force_login(get_user(1))

        data = {
            'mark': 1
        }
        start = time.time()
        response_card = self.client.post(reverse('api-card-mark', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_201_CREATED)
        self.assertLess(end-start, optimal_response_time)

    def test_set_card_marks_unauthorized(self):
        self.client.force_login(get_user(2))

        data = {
            'mark': 1,
        }
        start = time.time()
        response_card = self.client.post(reverse('api-card-mark', kwargs={'pk': 1}), data, format='json')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_delete_card_marks(self):
        self.client.force_login(get_user(1))

        data = [
            {'mark': 1}
        ]

        start = time.time()
        response_card = self.client.delete(reverse('api-card-mark-detail', kwargs={'pk': 1}), data, format='json',
                                           content_type='application/json')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_204_NO_CONTENT)
        self.assertLess(end-start, optimal_response_time)

    def test_delete_card_marks_unauthorized(self):
        self.client.force_login(get_user(2))

        data = [
            {'mark': 1}
        ]

        start = time.time()
        response_card = self.client.delete(reverse('api-card-mark-detail', kwargs={'pk': 1}), data, format='json',
                                           content_type='application/json')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_set_card_files(self):
        self.client.force_login(get_user(1))

        data = {'file': get_file()}
        start = time.time()
        response_card = self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_201_CREATED)
        self.assertLess(end-start, optimal_response_time)

    def test_set_card_files_unauthorized(self):
        self.client.force_login(get_user(2))

        data = {'file': get_file()}
        start = time.time()
        response_card = self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')
        end = time.time()

        self.assertEqual(response_card.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_delete_card_files(self):
        self.client.force_login(get_user(1))

        data = {'file': get_file()}
        self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')
        self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')

        data = [
            {'file': 1},
            {'file': 2}
        ]
        start = time.time()
        response = self.client.delete(reverse('api-card-file-detail', kwargs={'pk': 1}), data, format='json',
                                      content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertLess(end-start, optimal_response_time)

    def test_delete_card_files_unauthorized(self):
        self.client.force_login(get_user(2))

        data = {'file': get_file()}
        self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')
        self.client.post(reverse('api-card-file', kwargs={'pk': 1}), data, format='formdata')

        data = [
            {'file': 1},
            {'file': 2}
        ]
        start = time.time()
        response = self.client.delete(reverse('api-card-file-detail', kwargs={'pk': 1}), data, format='json',
                                      content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_create_card_comments(self):
        self.client.force_login(get_user(1))

        data = {'body': 'lorem ipsum'}

        start = time.time()
        response = self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                                    content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(end-start, optimal_response_time)

    def test_create_card_comments_unauthorized(self):
        self.client.force_login(get_user(2))

        data = {'body': 'lorem ipsum'}

        start = time.time()
        response = self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                                    content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_create_card_comments_update(self):
        self.client.force_login(get_user(1))

        data = {'body': 'lorem ipsum'}
        response = self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                                    content_type='application/json')

        data = {'body': 'lorem not ipsum'}
        start = time.time()
        response = self.client.put(reverse('api-card-comment-detail', kwargs={'pk': 1}), data, format='json',
                                   content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(end-start, optimal_response_time)

    def test_create_card_comments_update_unowned(self):
        self.client.force_login(get_user(1))
        self.client.post(reverse('api-board-add-member', kwargs={'pk': 1}), {'user': 'n2@user.com'}, format='json')

        data = {'body': 'lorem ipsum'}
        self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                         content_type='application/json')

        self.client.force_login(get_user(2))
        data = {'body': 'lorem not ipsum'}
        start = time.time()
        response = self.client.put(reverse('api-card-comment-detail', kwargs={'pk': 1}), data, format='json',
                                   content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertLess(end-start, optimal_response_time)

    def test_delete_comments(self):
        self.client.force_login(get_user(1))

        data = {'body': 'lorem ipsum'}
        self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                         content_type='application/json')
        self.client.post(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                         content_type='application/json')

        data = [
            {'id': 1},
            {'id': 2},
        ]

        start = time.time()
        response = self.client.delete(reverse('api-card-comment', kwargs={'pk': 1}), data, format='json',
                                      content_type='application/json')
        end = time.time()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertLess(end-start, optimal_response_time)
