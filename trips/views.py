from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import Trip, SalaryRecord, AuditLog
from .serializers import TripSerializer, TripCreateSerializer, TripUpdateSerializer, SalaryRecordSerializer, AuditLogSerializer
from .utils import AuditLogMixin

class TripListView(AuditLogMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip_type', 'status', 'driver', 'date']
    search_fields = ['trip_code', 'driver__user__first_name', 'driver__user__last_name', 'start_place', 'pickup_place']
    ordering_fields = ['date', 'created_at', 'trip_code']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Trip.objects.all()
        return Trip.objects.filter(driver__user=user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TripCreateSerializer
        return TripSerializer

class TripDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Trip.objects.all()
        return Trip.objects.filter(driver__user=user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TripUpdateSerializer
        return TripSerializer

class SalaryRecordListView(AuditLogMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalaryRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return SalaryRecord.objects.all()
        return SalaryRecord.objects.filter(driver__user=user)
    
    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionError("Only admins can create salary records")
        super().perform_create(serializer)

class SalaryRecordDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SalaryRecordSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return SalaryRecord.objects.all()
        return SalaryRecord.objects.filter(driver__user=user)

class AuditLogListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'table_name']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return AuditLog.objects.all()
        return AuditLog.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_summary(request):
    range_type = request.query_params.get('range', 'monthly')
    
    now = datetime.now()
    if range_type == 'weekly':
        start_date = now - timedelta(days=7)
    elif range_type == 'yearly':
        start_date = now - timedelta(days=365)
    else:  # monthly
        start_date = now - timedelta(days=30)
    
    trips = Trip.objects.filter(date__gte=start_date, status='completed')
    
    total_income = trips.aggregate(Sum('red_taxi_income'))['red_taxi_income__sum'] or 0
    total_expense = trips.aggregate(Sum('total_expense'))['total_expense__sum'] or 0
    total_profit = total_income - total_expense
    
    taxi_trips = trips.filter(trip_type='taxi').count()
    local_trips = trips.filter(trip_type='local').count()
    
    return Response({
        'range': range_type,
        'start_date': start_date.date(),
        'end_date': now.date(),
        'total_income': total_income,
        'total_expense': total_expense,
        'total_profit': total_profit,
        'taxi_trips': taxi_trips,
        'local_trips': local_trips,
        'total_trips': taxi_trips + local_trips
    })
