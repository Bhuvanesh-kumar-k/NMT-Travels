from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize default admin user with forced password change'

    def handle(self, *args, **options):
        username = 'Admin'
        password = 'Admin@123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists.')
            )
            return
        
        user = User.objects.create_user(
            username=username,
            email='admin@nmttravels.com',
            password=password,
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True,
            is_superuser=True,
            must_change_password=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user "{username}" with password "{password}". '
                'User will be required to change password on first login.'
            )
        )
