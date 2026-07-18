from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Driver

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'must_change_password']
        read_only_fields = ['id', 'role']

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Driver
        fields = ['id', 'user', 'user_id', 'licence_no', 'phone', 'alt_phone', 'address', 
                  'bank_account', 'ifsc', 'gpay_number', 'pf_no', 'current_trip_code', 
                  'last_trip_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DriverCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    phone = serializers.CharField(write_only=True)
    
    class Meta:
        model = Driver
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'phone',
                  'licence_no', 'alt_phone', 'address', 'bank_account', 'ifsc', 
                  'gpay_number', 'pf_no']
    
    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
            'phone': validated_data.pop('phone'),
            'role': 'driver'
        }
        user = User.objects.create_user(**user_data)
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class AdminResetDriverPasswordSerializer(serializers.Serializer):
    driver_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
