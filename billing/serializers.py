from rest_framework import serializers
from .models import Bill
from trips.serializers import TripSerializer

class BillSerializer(serializers.ModelSerializer):
    trip = TripSerializer(read_only=True)
    trip_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Bill
        fields = '__all__'
        read_only_fields = ['id', 'bill_code', 'generated_at', 'total_amount']
