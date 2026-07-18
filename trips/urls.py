from django.urls import path
from .views import (
    TripListView, TripDetailView, SalaryRecordListView, 
    SalaryRecordDetailView, AuditLogListView, reports_summary
)

urlpatterns = [
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('salary/', SalaryRecordListView.as_view(), name='salary-list'),
    path('salary/<int:pk>/', SalaryRecordDetailView.as_view(), name='salary-detail'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),
    path('reports/summary/', reports_summary, name='reports-summary'),
]
