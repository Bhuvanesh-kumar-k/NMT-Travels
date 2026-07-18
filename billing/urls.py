from django.urls import path
from .views import BillListView, BillDetailView, generate_bill_pdf

urlpatterns = [
    path('bills/', BillListView.as_view(), name='bill-list'),
    path('bills/<int:pk>/', BillDetailView.as_view(), name='bill-detail'),
    path('bills/generate/<int:trip_id>/', generate_bill_pdf, name='generate-bill-pdf'),
]
