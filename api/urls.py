from django.urls import path, include
from .views import BoardView, BoardDetailView, BarView

urlpatterns = [
    path('auth/', include('rest_auth.urls')),
    path('boards/', BoardView.as_view(), name='boards'),
    path('board/<int:pk>/', BoardDetailView.as_view(), name='board-details'),

    path('/bars/', BarView.as_view(), name='bars')
]