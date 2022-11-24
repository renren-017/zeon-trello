from django.urls import path
from .views import BoardListView, BoardDetailView, BoardCreateView, BoardUpdateView, BoardDeleteView,\
    CardCreateView, CardUpdateView, CardDetailView, CardDeleteView, CardLabelCreateView, CardFileCreateView

urlpatterns = [
    path('', BoardListView.as_view(), name='home'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path("board/add/", BoardCreateView.as_view(), name="board-add"),
    path("board/<int:pk>/update/", BoardUpdateView.as_view(), name='board-update'),
    path("board/<int:pk>/delete/", BoardDeleteView.as_view(), name='board-delete'),

    # Card Views
    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/<int:pk>",
        CardDetailView.as_view(),
        name="card-detail"),
    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/add/",
        CardCreateView.as_view(),
        name="card-add",
    ),
    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/<int:pk>/update/",
        CardUpdateView.as_view(),
        name="card-update",
    ),
    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/<int:pk>/delete/",
        CardDeleteView.as_view(),
        name="card-delete",
    ),

    # Card Assets Views
    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/<int:pk>/label/add",
        CardLabelCreateView.as_view(),
        name="card-label-add",
    ),

    path(
        "board/<int:board_id>/bar/<int:bar_id>/card/<int:pk>/document/add",
        CardFileCreateView.as_view(),
        name="card-file-add",
    ),
]
