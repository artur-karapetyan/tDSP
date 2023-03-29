from functools import wraps

from django.http import HttpResponse

from .user_auth import user_auth


def is_authorized(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not user_auth(request):
            return HttpResponse('Unauthorized', status=401)
        return func(request, *args, **kwargs)

    return wrapper
