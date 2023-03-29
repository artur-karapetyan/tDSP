from functools import wraps

import jwt
from django.contrib.auth.models import User
from django.http import HttpResponse

from .user_auth import user_auth
from ..models import GenericUser


def admin_authorized(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        is_auth = user_auth(request)
        if is_auth:
            user_info = jwt.decode(request.META.get("HTTP_AUTHORIZATION").split()[1], "SECRET_KEY",
                                   algorithms=["HS256"])
            user = User.objects.get(username=user_info["username"])
            generic_user = GenericUser.objects.get(user=user)
            if not generic_user.user.is_superuser:
                return HttpResponse('Unauthorized', status=307)
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=307)

    return wrapper
