from django.urls import path, include
from .views import BoardView, BoardDetailView, BarView, BarDetailView, \
    CardView, CardDetailView, CardLabelView, CardLabelDetailView,\
    CardFileView, CardFileDetailView, CardCommentView, CardChecklistView, StarredBoardsView

urlpatterns = [
    path('auth/', include('rest_auth.urls')),

    path('boards/', BoardView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('boards/starred', StarredBoardsView.as_view(), name='boards-starred'),

    path('bars/', BarView.as_view(), name='bars'),
    path('bars/<int:pk>', BarDetailView.as_view(), name='bar=detail'),

    path('cards/', CardView.as_view(), name='cards'),
    path('cards/<int:pk>', CardDetailView.as_view(), name='card-detail'),

    path('card_labels/', CardLabelView.as_view(), name='card-labels'),
    path('card_labels/<int:pk>', CardLabelDetailView.as_view(), name='card-label-detail'),

    path('card_files/', CardFileView.as_view(), name='card-files'),
    path('card_files/<int:pk>', CardFileDetailView.as_view(), name='card-file-detail'),

    path('card_comments/', CardCommentView.as_view(), name='card-comments'),

    path('card_checklists/>', CardChecklistView.as_view(), name='card-checklists'),
]