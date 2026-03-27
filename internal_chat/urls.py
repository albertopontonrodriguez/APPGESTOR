from django.urls import path

from .views import ChatMessageCreateView, ChatRoomCreateView, ChatRoomDeleteView, ChatRoomDetailView, ChatRoomListView

app_name = 'internal_chat'

urlpatterns = [
    path('', ChatRoomListView.as_view(), name='rooms'),
    path('salas/nueva/', ChatRoomCreateView.as_view(), name='room_create'),
    path('salas/<int:pk>/', ChatRoomDetailView.as_view(), name='room_detail'),
    path('salas/<int:pk>/mensaje/', ChatMessageCreateView.as_view(), name='message_create'),
    path('salas/<int:pk>/eliminar/', ChatRoomDeleteView.as_view(), name='room_delete'),
]
