from django.urls import path

from .views import BookingCreateView, BookingDetailView, BookingListView, BookingPaymentCreateView, BookingUpdateView

app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='list'),
    path('nuevo/', BookingCreateView.as_view(), name='create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', BookingUpdateView.as_view(), name='update'),
    path('<int:pk>/pagos/nuevo/', BookingPaymentCreateView.as_view(), name='payment_create'),
]
