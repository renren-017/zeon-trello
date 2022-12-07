from django.urls import path

from .views import (ProjectListView, ProjectDetailView, ProjectCreateView,
                    BoardDetailView, BoardCreateView, BoardUpdateView, BoardDeleteView,
                    BoardFavRedirectView, BoardFavRemoveRedirectView, BoardArchiveRedirectView,
                    BoardArchiveRemoveRedirectView,
                    CardCreateView, CardUpdateView, CardDetailView, CardDeleteView, SearchResultsView,)
from .asset_views import CardMarkCreateView, CardFileCreateView, CardCommentCreateView

urlpatterns = [
    # Boards
    path("projects/", ProjectListView.as_view(), name='home'),
    path("project/add/", ProjectCreateView.as_view(), name='project-add'),
    path("project/<int:pk>/", ProjectDetailView.as_view(), name='project-detail'),

    path("board/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),

    path("board/<int:pk>/favourite", BoardFavRedirectView.as_view(), name="board-fav"),
    path("board/<int:pk>/favourite/remove", BoardFavRemoveRedirectView.as_view(), name="board-fav-remove"),
    path("board/<int:pk>/archive", BoardArchiveRedirectView.as_view(), name="board-archive"),
    path("board/<int:pk>/archive/remove", BoardArchiveRemoveRedirectView.as_view(), name="board-archive-remove"),

    path("project/<int:pk>/board/add/", BoardCreateView.as_view(), name="board-add"),
    path("board/<int:pk>/update/", BoardUpdateView.as_view(), name="board-update"),
    path("board/<int:pk>/delete/", BoardDeleteView.as_view(), name="board-delete"),

    # Cards
    path("card/<int:pk>/", CardDetailView.as_view(), name="card-detail"),
    path("bar/<int:pk>/card/add/", CardCreateView.as_view(), name="card-add"),
    path("card/<int:pk>/update/", CardUpdateView.as_view(), name="card-update"),
    path("card/<int:pk>/delete/", CardDeleteView.as_view(), name="card-delete"),

    # Card Marks
    path("card/<int:pk>/label/add/", CardMarkCreateView.as_view(), name="card-mark-add"),
    # path("card_label/<int:pk>/delete/", CardLabelDeleteView.as_view(), name="card-label-delete"),

    # Card Files
    # path("card_file/<int:pk>/", CardFileDetailView.as_view(), name="card-file-detail"),
    path("card/<int:pk>/file/add/", CardFileCreateView.as_view(), name="card-file-add"),
    # path("card_file/<int:pk>/update/", CardFileUpdateView.as_view(), name="card-file-update"),
    # path("card_file/<int:pk>/delete/", CardFileDeleteView.as_view(), name="card-file-delete"),

    path("card/<int:pk>/comment/add/", CardCommentCreateView.as_view(), name="card-comment-add"),

    # Search
    path("search/", SearchResultsView.as_view(), name="search_results"),
]
