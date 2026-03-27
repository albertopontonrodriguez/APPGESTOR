from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from apps.notifications.services import notify_internal_chat_message

from .forms import ChatMessageForm, ChatRoomForm
from .models import ChatMessage, ChatRoom

User = get_user_model()


class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'internal_chat/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = ChatRoom.objects.filter(is_active=True, participants=self.request.user).annotate(
            messages_count=Count('messages'),
            last_activity=Max('messages__created_at'),
        ).distinct().order_by('-last_activity', 'name')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(participants__display_name__icontains=q) | Q(participants__username__icontains=q)).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        context['active_rooms_count'] = self.get_queryset().count()
        context['recent_messages_count'] = ChatMessage.objects.filter(room__participants=self.request.user).count()
        return context


class ChatRoomCreateView(LoginRequiredMixin, CreateView):
    model = ChatRoom
    form_class = ChatRoomForm
    template_name = 'internal_chat/room_form.html'
    success_url = reverse_lazy('internal_chat:rooms')

    def form_valid(self, form):
        room = form.save(commit=False)
        room.created_by = self.request.user
        room.save()
        form.save_m2m()
        room.participants.add(self.request.user)
        messages.success(self.request, 'Sala de chat creada correctamente.')
        return redirect('internal_chat:room_detail', pk=room.pk)


class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'internal_chat/room_detail.html'
    context_object_name = 'room'

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = ChatMessageForm()
        context['messages_list'] = self.object.messages.select_related('author').order_by('created_at')
        return context


class ChatMessageCreateView(LoginRequiredMixin, CreateView):
    form_class = ChatMessageForm
    template_name = 'internal_chat/message_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.room = get_object_or_404(ChatRoom.objects.filter(participants=request.user), pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        message_obj = form.save(commit=False)
        message_obj.room = self.room
        message_obj.author = self.request.user
        message_obj.save()
        notify_internal_chat_message(self.room, message_obj)
        messages.success(self.request, 'Mensaje enviado.')
        return redirect('internal_chat:room_detail', pk=self.room.pk)


class ChatRoomDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        room = get_object_or_404(ChatRoom, pk=kwargs['pk'], participants=request.user, is_active=True)
        if room.created_by_id != request.user.id and not getattr(request.user, 'is_admin_or_ceo', False):
            messages.error(request, 'No tienes permiso para eliminar esta sala.')
            return redirect('internal_chat:room_detail', pk=room.pk)
        room.is_active = False
        room.save(update_fields=['is_active'])
        messages.success(request, 'Chat eliminado correctamente.')
        return redirect('internal_chat:rooms')
