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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import os

def serve_react(request):
    """Serve the React app for all non-API routes"""
    print(f"=== SERVE_REACT CALLED ===")
    print(f"BASE_DIR: {settings.BASE_DIR}")
    
    try:
        # Try staticfiles first (production), then static (development)
        static_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'frontend', 'index.html')
        print(f"Trying staticfiles path: {static_path}")
        print(f"File exists: {os.path.exists(static_path)}")
        
        if not os.path.exists(static_path):
            static_path = os.path.join(settings.BASE_DIR, 'static', 'frontend', 'index.html')
            print(f"Trying static path: {static_path}")
            print(f"File exists: {os.path.exists(static_path)}")
        
        with open(static_path, 'r') as f:
            content = f.read()
            print(f"Successfully read index.html, length: {len(content)}")
            return HttpResponse(content, content_type='text/html')
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        return HttpResponse("React app not built. Run 'npm run build' in frontend directory.", status=503)
    except Exception as e:
        print(f"Exception in serve_react: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error serving React app: {str(e)}", status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('trips.urls')),
    path('api/', include('billing.urls')),
    re_path(r'^(?!api/|admin/).*$', serve_react),  # Serve React app for all other routes (catch-all, exclude api and admin)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
