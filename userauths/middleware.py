from core.models import UserActivity

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def process_template_response(self, request, response):
        if request.user.is_authenticated and request.path == '/checkout/':
            UserActivity.objects.create(user=request.user, activity='Initiated checkout')

        return response
    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            UserActivity.objects.create(user=request.user, activity=f'User accessed {request.path}')

        return response

