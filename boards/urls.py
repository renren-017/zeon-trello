from django.urls import path

from .views import BoardListView, BoardDetailView, BoardCreateView, BoardUpdateView, BoardDeleteView,\
    CardCreateView, CardUpdateView, CardDetailView, CardDeleteView, SearchResultsView
from .asset_views import CardLabelCreateView, CardFileCreateView, CardChecklistCreateView, CardCommentCreateView

urlpatterns = [
    # Boards
    path("boards/", BoardListView.as_view(), name='home'),
    path("board/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    path("board/add/", BoardCreateView.as_view(), name="board-add"),
    path("board/<int:pk>/update/", BoardUpdateView.as_view(), name="board-update"),
    path("board/<int:pk>/delete/", BoardDeleteView.as_view(), name="board-delete"),

    # Cards
    path("card/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
    path("bar/<int:pk>/card/add/", CardCreateView.as_view(), name="card-add"),
    path("card/<int:pk>/update/", CardUpdateView.as_view(), name="card-update"),
    path("card/<int:pk>/delete/", CardDeleteView.as_view(), name="card-delete"),

    # Card Labels
    # path("card_label/<int:pk>/", CardLabelDetailView.as_view(), name="card-label-detail"),
    path("card/<int:pk>/label/add/", CardLabelCreateView.as_view(), name="card-label-add"),
    # path("card_label/<int:pk>/update/", CardLabelUpdateView.as_view(), name="card-label-update"),
    # path("card_label/<int:pk>/delete/", CardLabelDeleteView.as_view(), name="card-label-delete"),

    # Card Files
    # path("card_file/<int:pk>/", CardFileDetailView.as_view(), name="card-file-detail"),
    path("card/<int:pk>/file/add/", CardFileCreateView.as_view(), name="card-file-add"),
    # path("card_file/<int:pk>/update/", CardFileUpdateView.as_view(), name="card-file-update"),
    # path("card_file/<int:pk>/delete/", CardFileDeleteView.as_view(), name="card-file-delete"),

    # Card Checklists
    # path("card_checklist/<int:pk>/", CardChecklistDetailView.as_view(), name="card-checklist-detail"),
    path("card/<int:pk>/checklist/add/", CardChecklistCreateView.as_view(), name="card-checklist-add"),
    # path("card_checklist/<int:pk>/update/", CardChecklistUpdateView.as_view(), name="card-checklist-update"),
    # path("card_checklist/<int:pk>/delete/", CardChecklistDeleteView.as_view(), name="card-checklist-delete"),

    path("card/<int:pk>/comment/add/", CardCommentCreateView.as_view(), name="card-comment-add"),

    # Search
    path("search/", SearchResultsView.as_view(), name="search_results"),
]
