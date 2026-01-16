import requests
from django.http import JsonResponse
import os
import json
from dotenv import load_dotenv

class OAuth2LoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        load_dotenv()
        if request.path == '/api/login/' and request.method == 'POST':
            try:
                data_in = json.loads(request.body)
                username = data_in.get('username')
                password = data_in.get('password')
            except Exception:
                username = request.POST.get('username')
                password = request.POST.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Thiếu username hoặc password'}, status=400)

            data = {
                'username': username,
                'password': password,
                'client_id': os.getenv('OAUTH2_CLIENT_ID'),
                'client_secret': os.getenv('OAUTH2_CLIENT_SECRET'),
                'grant_type': 'password'
            }

            print("DATA gửi lên:", data)

            response = requests.post('http://localhost:8000/o/token/', data=data)

            print("RESPONSE từ /o/token/:", response.status_code, response.text)

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse(response.json(), status=response.status_code)
        return self.get_response(request)