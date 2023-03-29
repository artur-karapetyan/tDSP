import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.http import require_POST

from ..models import GenericUser
from ..tools.jwt_tool import generate_jwt


class GenericUserView(View):

    @staticmethod
    @require_POST
    def login(request):
        data = json.loads(request.body.decode("utf-8"))

        try:
            username = data['username']
            password = data['password']
        except KeyError:
            return HttpResponse("Missing required fields", status=400)

        user = authenticate(username=username, password=password)
        if user:
            try:
                generic_user = GenericUser.objects.get(user=user)
            except ObjectDoesNotExist:
                return HttpResponse("User is not registered", status=400)

            login(request, user)
            jwt_token = generate_jwt(generic_user).decode('utf-8')

            if user.is_superuser:
                user_type = "Admin"
            else:
                user_type = "AdOps"

            return JsonResponse({"user_type": user_type, "access_token": jwt_token}, status=200)
        else:
            try:
                user = User.objects.get(username=username)
            except ObjectDoesNotExist:
                return HttpResponse("User is not registered", status=400)
            return HttpResponse("Wrong Password", status=400)

    @staticmethod
    @require_POST
    def logout(request):
        logout(request)
        return HttpResponse(
            json.dumps({"status": "ok"}), status=200, content_type="application/json"
        )
