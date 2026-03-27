from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from apps.brands.models import Brand
from apps.configuration.models import StatusCatalog
from apps.configuration.utils import get_currency_choices, get_status_choices
from apps.core.permissions import FinanceManageMixin
from apps.expenses.models import Supplier
from apps.reports.filters import filter_invoices_issued, filter_invoices_received
from apps.travelers.models import Traveler

from .forms import InvoiceIssuedAttachmentForm, InvoiceIssuedForm, InvoiceReceivedAttachmentForm, InvoiceReceivedForm
from .models import InvoiceIssued, InvoiceIssuedAttachment, InvoiceReceived, InvoiceReceivedAttachment


class BillingHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'billing/billing_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'issued_count': InvoiceIssued.objects.count(),
            'received_count': InvoiceReceived.objects.count(),
            'issued_total': InvoiceIssued.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
            'received_total': InvoiceReceived.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
            'issued_pending_total': InvoiceIssued.objects.exclude(status=InvoiceIssued.Status.PAID).aggregate(total=Sum('total_amount'))['total'] or 0,
            'recent_issued': InvoiceIssued.objects.select_related('brand', 'traveler').order_by('-issue_date', '-created_at')[:6],
            'recent_received': InvoiceReceived.objects.select_related('brand', 'supplier').order_by('-issue_date', '-created_at')[:6],
        })
        return context


class InvoiceIssuedListView(LoginRequiredMixin, ListView):
    model = InvoiceIssued
    template_name = 'billing/invoice_issued_list.html'
    context_object_name = 'invoices'
    paginate_by = 25

    def get_queryset(self):
        return filter_invoices_issued(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = filter_invoices_issued(self.request.GET)
        context.update({
            'query': self.request.GET.get('q', '').strip(),
            'selected_brand': self.request.GET.get('brand', '').strip(),
            'selected_traveler': self.request.GET.get('traveler', '').strip(),
            'selected_status': self.request.GET.get('status', '').strip(),
            'selected_currency': self.request.GET.get('currency', '').strip(),
            'date_from': self.request.GET.get('date_from', '').strip(),
            'date_to': self.request.GET.get('date_to', '').strip(),
            'brands': Brand.objects.order_by('name'),
            'travelers': Traveler.objects.order_by('last_name', 'first_name'),
            'status_choices': get_status_choices(StatusCatalog.StatusGroup.INVOICE_ISSUED, InvoiceIssued.Status.choices),
            'currencies': get_currency_choices(['EUR', 'USD']),
            'total_amount': filtered.aggregate(total=Sum('total_amount'))['total'] or 0,
        })
        return context


class InvoiceIssuedCreateView(FinanceManageMixin, CreateView):
    model = InvoiceIssued
    form_class = InvoiceIssuedForm
    template_name = 'billing/invoice_issued_form.html'
    success_url = reverse_lazy('billing:issued_list')


class InvoiceIssuedDetailView(LoginRequiredMixin, DetailView):
    model = InvoiceIssued
    template_name = 'billing/invoice_issued_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        return InvoiceIssued.objects.select_related('brand', 'traveler', 'booking', 'booking__trip')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_form'] = InvoiceIssuedAttachmentForm()
        return context


class InvoiceIssuedUpdateView(FinanceManageMixin, UpdateView):
    model = InvoiceIssued
    form_class = InvoiceIssuedForm
    template_name = 'billing/invoice_issued_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_form'] = InvoiceIssuedAttachmentForm()
        return context

    def get_success_url(self):
        return reverse_lazy('billing:issued_detail', kwargs={'pk': self.object.pk})


class InvoiceReceivedListView(LoginRequiredMixin, ListView):
    model = InvoiceReceived
    template_name = 'billing/invoice_received_list.html'
    context_object_name = 'invoices'
    paginate_by = 25

    def get_queryset(self):
        return filter_invoices_received(self.request.GET)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = filter_invoices_received(self.request.GET)
        context.update({
            'query': self.request.GET.get('q', '').strip(),
            'selected_brand': self.request.GET.get('brand', '').strip(),
            'selected_supplier': self.request.GET.get('supplier', '').strip(),
            'selected_currency': self.request.GET.get('currency', '').strip(),
            'date_from': self.request.GET.get('date_from', '').strip(),
            'date_to': self.request.GET.get('date_to', '').strip(),
            'brands': Brand.objects.order_by('name'),
            'suppliers': Supplier.objects.order_by('legal_name'),
            'currencies': get_currency_choices(['EUR', 'USD']),
            'total_amount': filtered.aggregate(total=Sum('total_amount'))['total'] or 0,
        })
        return context


class InvoiceReceivedCreateView(FinanceManageMixin, CreateView):
    model = InvoiceReceived
    form_class = InvoiceReceivedForm
    template_name = 'billing/invoice_received_form.html'
    success_url = reverse_lazy('billing:received_list')


class InvoiceReceivedDetailView(LoginRequiredMixin, DetailView):
    model = InvoiceReceived
    template_name = 'billing/invoice_received_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        return InvoiceReceived.objects.select_related('brand', 'supplier', 'expense', 'expense__trip')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_form'] = InvoiceReceivedAttachmentForm()
        return context


class InvoiceReceivedUpdateView(FinanceManageMixin, UpdateView):
    model = InvoiceReceived
    form_class = InvoiceReceivedForm
    template_name = 'billing/invoice_received_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attachment_form'] = InvoiceReceivedAttachmentForm()
        return context

    def get_success_url(self):
        return reverse_lazy('billing:received_detail', kwargs={'pk': self.object.pk})


class InvoiceIssuedAttachmentCreateView(FinanceManageMixin, CreateView):
    model = InvoiceIssuedAttachment
    form_class = InvoiceIssuedAttachmentForm

    def form_valid(self, form):
        form.instance.invoice = get_object_or_404(InvoiceIssued, pk=self.kwargs['pk'])
        messages.success(self.request, 'Adjunto añadido a la factura emitida.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo subir el adjunto. Revisa el archivo y los campos obligatorios.')
        return redirect('billing:issued_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('billing:issued_detail', kwargs={'pk': self.kwargs['pk']})


class InvoiceReceivedAttachmentCreateView(FinanceManageMixin, CreateView):
    model = InvoiceReceivedAttachment
    form_class = InvoiceReceivedAttachmentForm

    def form_valid(self, form):
        form.instance.invoice = get_object_or_404(InvoiceReceived, pk=self.kwargs['pk'])
        messages.success(self.request, 'Adjunto añadido a la factura recibida.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'No se pudo subir el adjunto. Revisa el archivo y los campos obligatorios.')
        return redirect('billing:received_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('billing:received_detail', kwargs={'pk': self.kwargs['pk']})


class InvoiceIssuedAttachmentDeleteView(FinanceManageMixin, View):
    def post(self, request, pk, attachment_pk):
        get_object_or_404(InvoiceIssuedAttachment, pk=attachment_pk, invoice_id=pk).delete()
        messages.success(request, 'Adjunto eliminado de la factura emitida.')
        return redirect('billing:issued_detail', pk=pk)


class InvoiceReceivedAttachmentDeleteView(FinanceManageMixin, View):
    def post(self, request, pk, attachment_pk):
        get_object_or_404(InvoiceReceivedAttachment, pk=attachment_pk, invoice_id=pk).delete()
        messages.success(request, 'Adjunto eliminado de la factura recibida.')
        return redirect('billing:received_detail', pk=pk)


def _draw_text_pair(pdf, x, y, label, value):
    pdf.setFont('Helvetica-Bold', 10)
    pdf.drawString(x, y, label)
    pdf.setFont('Helvetica', 10)
    pdf.drawString(x + 115, y, value)


def _right_text(pdf, x_right, y, text, font_name='Helvetica-Bold', font_size=14):
    pdf.setFont(font_name, font_size)
    width = stringWidth(text, font_name, font_size)
    pdf.drawString(x_right - width, y, text)


class InvoiceIssuedPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        invoice = InvoiceIssued.objects.select_related('brand', 'traveler', 'booking', 'booking__trip').get(pk=pk)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        pdf.setTitle(f'Factura {invoice.invoice_number}')
        pdf.setFont('Helvetica-Bold', 20)
        pdf.drawString(50, height - 60, 'FACTURA EMITIDA')
        _right_text(pdf, width - 50, height - 60, invoice.invoice_number)
        pdf.setStrokeColorRGB(0.72, 0.78, 0.68)
        pdf.line(50, height - 75, width - 50, height - 75)
        _draw_text_pair(pdf, 50, height - 110, 'Marca:', invoice.brand.name)
        _draw_text_pair(pdf, 50, height - 130, 'Fecha:', str(invoice.issue_date))
        _draw_text_pair(pdf, 50, height - 150, 'Viajero:', str(invoice.traveler))
        _draw_text_pair(pdf, 50, height - 170, 'Moneda:', invoice.currency)
        _draw_text_pair(pdf, 50, height - 190, 'Estado:', invoice.get_status_display())
        if invoice.booking:
            _draw_text_pair(pdf, 50, height - 210, 'Viaje:', invoice.booking.trip.name)
        box_top = height - 280
        pdf.roundRect(50, box_top - 120, width - 100, 120, 10, stroke=1, fill=0)
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(65, box_top - 25, 'Resumen económico')
        _draw_text_pair(pdf, 65, box_top - 50, 'Base imponible:', f'{invoice.taxable_base} {invoice.currency}')
        _draw_text_pair(pdf, 65, box_top - 72, 'IVA:', f'{invoice.vat_amount} {invoice.currency}')
        _draw_text_pair(pdf, 65, box_top - 94, 'Total:', f'{invoice.total_amount} {invoice.currency}')
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(50, box_top - 160, 'Notas')
        pdf.setFont('Helvetica', 10)
        text_obj = pdf.beginText(50, box_top - 180)
        for line in (invoice.notes or 'Sin notas').splitlines() or ['Sin notas']:
            text_obj.textLine(line)
        pdf.drawText(text_obj)
        pdf.setFont('Helvetica', 9)
        pdf.drawString(50, 40, 'Documento generado por GESTOR')
        pdf.showPage(); pdf.save(); buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="factura_emitida_{invoice.invoice_number}.pdf"'
        return response


class InvoiceReceivedPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        invoice = InvoiceReceived.objects.select_related('brand', 'supplier', 'expense', 'expense__trip').get(pk=pk)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        pdf.setTitle(f'Factura proveedor {invoice.invoice_number}')
        pdf.setFont('Helvetica-Bold', 20)
        pdf.drawString(50, height - 60, 'FACTURA RECIBIDA')
        _right_text(pdf, width - 50, height - 60, invoice.invoice_number)
        pdf.setStrokeColorRGB(0.72, 0.78, 0.68)
        pdf.line(50, height - 75, width - 50, height - 75)
        _draw_text_pair(pdf, 50, height - 110, 'Marca:', invoice.brand.name)
        _draw_text_pair(pdf, 50, height - 130, 'Fecha:', str(invoice.issue_date))
        _draw_text_pair(pdf, 50, height - 150, 'Proveedor:', str(invoice.supplier))
        _draw_text_pair(pdf, 50, height - 170, 'Moneda:', invoice.currency)
        if invoice.expense:
            _draw_text_pair(pdf, 50, height - 190, 'Gasto asociado:', str(invoice.expense.category))
            if invoice.expense.trip:
                _draw_text_pair(pdf, 50, height - 210, 'Viaje:', invoice.expense.trip.name)
        box_top = height - 280
        pdf.roundRect(50, box_top - 120, width - 100, 120, 10, stroke=1, fill=0)
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(65, box_top - 25, 'Resumen económico')
        _draw_text_pair(pdf, 65, box_top - 50, 'Base imponible:', f'{invoice.taxable_base} {invoice.currency}')
        _draw_text_pair(pdf, 65, box_top - 72, 'IVA:', f'{invoice.vat_amount} {invoice.currency}')
        _draw_text_pair(pdf, 65, box_top - 94, 'Total:', f'{invoice.total_amount} {invoice.currency}')
        pdf.setFont('Helvetica-Bold', 11)
        pdf.drawString(50, box_top - 160, 'Notas')
        pdf.setFont('Helvetica', 10)
        text_obj = pdf.beginText(50, box_top - 180)
        for line in (invoice.notes or 'Sin notas').splitlines() or ['Sin notas']:
            text_obj.textLine(line)
        pdf.drawText(text_obj)
        pdf.setFont('Helvetica', 9)
        pdf.drawString(50, 40, 'Documento generado por GESTOR')
        pdf.showPage(); pdf.save(); buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="factura_recibida_{invoice.invoice_number}.pdf"'
        return response
