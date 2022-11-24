from django.urls import path
from .views import BoardListView, BoardDetailView, BoardCreateView, CardCreateView, CardUpdateView, CardDetailView

urlpatterns = [
    path('', BoardListView.as_view(), name='home'),
    path('<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path("board/add/", BoardCreateView.as_view(), name="board-add"),

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
]
