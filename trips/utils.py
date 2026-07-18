from django.db import models
from trips.models import AuditLog
from django.contrib.auth import get_user_model

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
