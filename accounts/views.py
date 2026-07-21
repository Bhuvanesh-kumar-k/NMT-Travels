from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import secrets
import hashlib
from .models import Driver
from trips.models import AuditLog
from .serializers import (
    UserSerializer, DriverSerializer, DriverCreateSerializer,
    LoginSerializer, ChangePasswordSerializer, ForgotPasswordSerializer,
    AdminResetDriverPasswordSerializer
)

User = get_user_model()

class AuditLogMixin:
    """Mixin to automatically log CRUD operations"""
    
    def perform_create(self, serializer):
        instance = serializer.save()
        self._log_audit('create', instance)
        return instance
    
    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_data = self._serialize_instance(old_instance)
        instance = serializer.save()
        new_data = self._serialize_instance(instance)
        
        # Log changes
        changes = {}
        for field in old_data:
            if old_data[field] != new_data.get(field):
                changes[field] = {
                    'old': old_data[field],
                    'new': new_data.get(field)
                }
        
        if changes:
            self._log_audit('update', instance, changes)
        
        return instance
    
    def perform_destroy(self, instance):
        old_data = self._serialize_instance(instance)
        self._log_audit('delete', instance, old_data)
        instance.delete()
    
    def _log_audit(self, action, instance, changes=None):
        """Create an audit log entry"""
        table_name = instance._meta.db_table
        
        AuditLog.objects.create(
            user=self.request.user,
            action=action,
            table_name=table_name,
            record_id=instance.id,
            changes=changes or {},
            ip_address=self._get_client_ip()
        )
    
    def _serialize_instance(self, instance):
        """Serialize model instance to dictionary"""
        data = {}
        for field in instance._meta.fields:
            field_name = field.name
            value = getattr(instance, field_name)
            
            # Convert datetime/date/time to string
            if hasattr(value, 'isoformat'):
                data[field_name] = value.isoformat()
            elif isinstance(value, models.Model):
                data[field_name] = value.id
            else:
                data[field_name] = value
        
        return data
    
    def _get_client_ip(self):
        """Get client IP address"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    print(f"DEBUG: login_view called with method: {request.method}")
    print(f"DEBUG: Request data: {request.data}")
    print(f"DEBUG: Request content type: {request.content_type}")
    print(f"DEBUG: Request headers: {dict(request.headers)}")
    
    try:
        serializer = LoginSerializer(data=request.data)
        print(f"DEBUG: Serializer created: {serializer}")
        
        if not serializer.is_valid():
            print(f"DEBUG: Serializer validation failed: {serializer.errors}")
            return Response(
                {'error': 'Invalid request data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        print(f"DEBUG: Username: {username}")
        
        user = authenticate(username=username, password=password)
        print(f"DEBUG: Authenticated user: {user}")
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'error': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'must_change_password': user.must_change_password
        })
    except Exception as e:
        print(f"DEBUG: Exception in login_view: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.must_change_password = False
        user.save()
        
        return Response({'message': 'Password changed successfully'})

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prevent Admin from self-resetting password
        if user.role == 'admin':
            return Response(
                {'error': 'Admin users cannot reset their own password. Please contact the developer for assistance.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Change password
        user.set_password(new_password)
        user.must_change_password = True  # Force password change on next login
        user.save()
        
        return Response({'message': 'Password changed successfully. Please login with your new password.'})

class AdminResetDriverPasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminResetDriverPasswordSerializer
    
    def post(self, request):
        # Only admin can reset driver passwords
        if request.user.role != 'admin':
            return Response(
                {'error': 'Only admins can reset driver passwords'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        driver_id = serializer.validated_data['driver_id']
        new_password = serializer.validated_data['new_password']
        
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Driver not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Reset password and force change on next login
        driver.user.set_password(new_password)
        driver.user.must_change_password = True
        driver.user.save()
        
        return Response({'message': 'Driver password reset successfully. Driver will need to change password on next login.'})

class DriverListView(AuditLogMixin, generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Driver.objects.all()
        return Driver.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DriverCreateSerializer
        return DriverSerializer
    
    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionError("Only admins can create drivers")
        super().perform_create(serializer)

class DriverDetailView(AuditLogMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DriverSerializer
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Driver.objects.all()
        return Driver.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionError("Only admins can update drivers")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        if self.request.user.role != 'admin':
            raise PermissionError("Only admins can delete drivers")
        super().perform_destroy(instance)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
