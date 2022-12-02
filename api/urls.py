from django.urls import path, include
from .views import (BoardView, BoardDetailView,
                    BarView, BarDetailView,
                    CardView, CardDetailView,
                    CardLabelView, CardLabelDetailView,
                    CardFileView, CardFileDetailView,
                    CardCommentView,
                    CardChecklistView, BoardsFavouriteDetailView, BoardsFavouriteView,
                    ProjectView, ProjectDetailView, ProjectBoardView)

urlpatterns = [
    path('auth/', include('rest_auth.urls')),

    path('projects/', ProjectView.as_view(), name='api-projects'),
    path('projects/<int:pk>', ProjectDetailView.as_view(), name='api-project-detail'),
    path('projects/<int:pk>/boards/', ProjectBoardView.as_view(), name='api-project-boards'),

    path('boards/', BoardView.as_view(), name='api-boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='api-board-detail'),
    path('boards/<int:pk>/favourite/', BoardsFavouriteDetailView.as_view(), name='api-board-favourite'),
    path('boards/favourite/', BoardsFavouriteView.as_view(), name='api-boards-favourite'),

    path('bars/', BarView.as_view(), name='api-bars'),
    path('bars/<int:pk>', BarDetailView.as_view(), name='api-bar-detail'),

    path('cards/', CardView.as_view(), name='api-cards'),
    path('cards/<int:pk>', CardDetailView.as_view(), name='api-card-detail'),

    path('card_labels/', CardLabelView.as_view(), name='api-card-labels'),
    path('card_labels/<int:pk>', CardLabelDetailView.as_view(), name='api-card-label-detail'),

    path('card_files/', CardFileView.as_view(), name='api-card-files'),
    path('card_files/<int:pk>', CardFileDetailView.as_view(), name='api-card-file-detail'),

    path('card_comments/', CardCommentView.as_view(), name='api-card-comments'),

    path('card_checklists/>', CardChecklistView.as_view(), name='api-card-checklists'),
]