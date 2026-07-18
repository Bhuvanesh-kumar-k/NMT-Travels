from rest_framework import serializers
from .models import Trip, SalaryRecord, AuditLog
from accounts.serializers import DriverSerializer

class TripSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ['id', 'trip_code', 'total_km', 'total_time', 'net_red_income', 
                          'salary', 'main_salary', 'total_expense', 'balance_amount', 
                          'bonus', 'total_advance', 'created_at', 'updated_at']

class TripCreateSerializer(serializers.ModelSerializer):
    driver_id = serializers.IntegerField()
    
    class Meta:
        model = Trip
        fields = ['trip_type', 'date', 'day', 'driver_id', 'start_place', 'pickup_place', 
                  'drop_place', 'start_km', 'time_in', 'cng', 'petrol', 'red_taxi_income', 
                  'commission', 'advance', 'advance_received_today', 'waiting_charge', 
                  'inter_state_permit', 'luggage_charges', 'pet_charges', 'hill_charges', 
                  'toll_charges', 'base_fare', 'driver_allowance', 'previous_salary', 
                  'dr_adv', 'salary_per_hour', 'status']
    
    def create(self, validated_data):
        from datetime import datetime
        # Generate trip code: YYYY + 8-digit sequence
        year = datetime.now().year
        last_trip = Trip.objects.filter(trip_code__startswith=str(year)).order_by('-trip_code').first()
        if last_trip:
            last_seq = int(last_trip.trip_code[-8:])
            new_seq = last_seq + 1
        else:
            new_seq = 10000000
        trip_code = f"{year}{new_seq:08d}"
        
        validated_data['trip_code'] = trip_code
        trip = Trip.objects.create(**validated_data)
        
        # Update driver's current trip code
        driver = trip.driver
        driver.current_trip_code = trip_code
        driver.save()
        
        return trip

class TripUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['end_place', 'end_km', 'time_out', 'cng', 'petrol', 'red_taxi_income', 
                  'commission', 'advance', 'advance_received_today', 'waiting_charge', 
                  'inter_state_permit', 'luggage_charges', 'pet_charges', 'hill_charges', 
                  'toll_charges', 'base_fare', 'driver_allowance', 'previous_salary', 
                  'dr_adv', 'salary_per_hour', 'status']
    
    def update(self, instance, validated_data):
        # Check if trip is completed and user is not admin
        if instance.status == 'completed' and self.context['request'].user.role != 'admin':
            raise serializers.ValidationError("Cannot edit completed trips")
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # If trip is completed, update driver's last trip code
        if instance.status == 'completed':
            driver = instance.driver
            driver.last_trip_code = instance.trip_code
            driver.current_trip_code = None
            driver.save()
        
        return instance

class SalaryRecordSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SalaryRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
