from django import forms

from .models import ChatMessage, ChatRoom


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'participants', 'is_active']
        labels = {
            'name': 'Nombre de la sala',
            'description': 'Descripción',
            'participants': 'Participantes',
            'is_active': 'Activa',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'participants': forms.SelectMultiple(attrs={'size': 8}),
        }


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['body', 'attachment']
        labels = {
            'body': 'Mensaje',
            'attachment': 'Adjunto',
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe un mensaje interno para el equipo…'}),
        }
