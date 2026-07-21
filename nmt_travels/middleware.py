import logging
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"=== REQUEST START ===")
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")
        print(f"GET params: {dict(request.GET)}")
        print(f"POST data: {dict(request.POST)}")
        print(f"Body: {request.body}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Meta: {request.META}")
        print(f"=== REQUEST END ===")
        
        response = self.get_response(request)
        
        print(f"=== RESPONSE START ===")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.get('Content-Type', 'N/A')}")
        print(f"=== RESPONSE END ===")
        
        return response
