"""
URL configuration for nmt_travels project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def serve_react(request):
    """Serve the React app"""
    try:
        # Try staticfiles first (production), then static (development)
        static_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'frontend', 'index.html')
        if not os.path.exists(static_path):
            static_path = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
        
        with open(static_path, 'r') as f:
            content = f.read()
            return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("React app not built. Run 'npm run build' in frontend directory.", status=503)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('trips.urls')),
    path('api/', include('billing.urls')),
    path('', serve_react),  # Serve React app for all other routes
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
