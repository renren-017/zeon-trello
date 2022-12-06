from django.urls import path, re_path, include
from .views import (BoardView, BoardDetailView,
                    ColumnView, ColumnDetailView,
                    CardView, CardDetailView,
                    CardMarkView, CardMarkDetailView,
                    BoardMarkView, BoardMarkDetailView,
                    CardFileView, CardFileDetailView,
                    CardCommentView,
                    BoardsFavouriteView, BoardsFavouriteView, BoardsLastSeenView,
                    ProjectView, ProjectDetailView, ProjectBoardView, BoardMemberAddView, CardCommentDetailView)


urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),

    path('projects/', ProjectView.as_view(), name='api-projects'),
    path('projects/<int:pk>', ProjectDetailView.as_view(), name='api-project-detail'),

    path('boards/project/<int:pk>/', ProjectBoardView.as_view(), name='api-project-boards'),
    path('boards/', BoardView.as_view(), name='api-boards'),
    path('boards/favourite/', BoardsFavouriteView.as_view(), name='api-boards-favourite'),
    path('boards/recent/', BoardsLastSeenView.as_view(), name='api-boards-recent'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='api-board-detail'),
    path('boards/<int:pk>/invite/', BoardMemberAddView.as_view(), name='api-board-add-member'),
    path('boards/favourite/', BoardsFavouriteView.as_view(), name='api-board-favourite'),

    path('columns/board/<int:pk>/', ColumnView.as_view(), name='api-columns'),
    path('columns/<int:pk>/', ColumnDetailView.as_view(), name='api-column-detail'),

    path('cards/column/<int:pk>/', CardView.as_view(), name='api-cards'),
    path('cards/<int:pk>/', CardDetailView.as_view(), name='api-card-detail'),

    path('mark/board/<int:pk>/', BoardMarkView.as_view(), name='api-board-mark'),
    path('mark/<int:pk>/', BoardMarkDetailView.as_view(), name='api-board-mark-detail'),
    path('mark/card/<int:pk>/', CardMarkView.as_view(), name='api-card-mark'),
    path('card_marks/card/<int:pk>/delete', CardMarkDetailView.as_view(), name='api-card-mark-detail'),

    path('files/card/<int:pk>/', CardFileView.as_view(), name='api-card-file'),
    path('files/card/<int:pk>/delete', CardFileDetailView.as_view(), name='api-card-file-detail'),

    path('comments/card/<int:pk>/', CardCommentView.as_view(), name='api-card-comment'),
    path('comments/<int:pk>/', CardCommentDetailView.as_view(), name='api-card-comment-detail')
]