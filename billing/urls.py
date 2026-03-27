from django.urls import path

from .views import (
    BillingHomeView, InvoiceIssuedAttachmentCreateView, InvoiceIssuedAttachmentDeleteView,
    InvoiceIssuedCreateView, InvoiceIssuedDetailView, InvoiceIssuedListView, InvoiceIssuedPDFView,
    InvoiceIssuedUpdateView, InvoiceReceivedAttachmentCreateView, InvoiceReceivedAttachmentDeleteView,
    InvoiceReceivedCreateView, InvoiceReceivedDetailView, InvoiceReceivedListView, InvoiceReceivedPDFView,
    InvoiceReceivedUpdateView,
)

app_name = 'billing'

urlpatterns = [
    path('', BillingHomeView.as_view(), name='home'),
    path('emitidas/', InvoiceIssuedListView.as_view(), name='issued_list'),
    path('emitidas/nueva/', InvoiceIssuedCreateView.as_view(), name='issued_create'),
    path('emitidas/<int:pk>/', InvoiceIssuedDetailView.as_view(), name='issued_detail'),
    path('emitidas/<int:pk>/editar/', InvoiceIssuedUpdateView.as_view(), name='issued_update'),
    path('emitidas/<int:pk>/pdf/', InvoiceIssuedPDFView.as_view(), name='issued_pdf'),
    path('emitidas/<int:pk>/adjuntos/nuevo/', InvoiceIssuedAttachmentCreateView.as_view(), name='issued_attachment_create'),
    path('emitidas/<int:pk>/adjuntos/<int:attachment_pk>/eliminar/', InvoiceIssuedAttachmentDeleteView.as_view(), name='issued_attachment_delete'),
    path('recibidas/', InvoiceReceivedListView.as_view(), name='received_list'),
    path('recibidas/nueva/', InvoiceReceivedCreateView.as_view(), name='received_create'),
    path('recibidas/<int:pk>/', InvoiceReceivedDetailView.as_view(), name='received_detail'),
    path('recibidas/<int:pk>/editar/', InvoiceReceivedUpdateView.as_view(), name='received_update'),
    path('recibidas/<int:pk>/pdf/', InvoiceReceivedPDFView.as_view(), name='received_pdf'),
    path('recibidas/<int:pk>/adjuntos/nuevo/', InvoiceReceivedAttachmentCreateView.as_view(), name='received_attachment_create'),
    path('recibidas/<int:pk>/adjuntos/<int:attachment_pk>/eliminar/', InvoiceReceivedAttachmentDeleteView.as_view(), name='received_attachment_delete'),
]
