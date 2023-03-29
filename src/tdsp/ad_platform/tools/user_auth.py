from datetime import datetime

import jwt
from django.contrib.auth.models import User

from ..models import GenericUser


def user_auth(request):
    try:
        token = request.META.get("HTTP_AUTHORIZATION").split()[1]
    except:
        return False

    try:
        user_info = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user = User.objects.get(username=user_info["username"])
        GenericUser.objects.get(user=user)
    except:
        return False

    # Convert expiration string to datetime object
    expiration_datetime = datetime.strptime(user_info['expiration'], '%Y-%m-%d %H:%M:%S.%f')

    # Get current time in UTC
    current_time = datetime.utcnow()

    if expiration_datetime > current_time:
        return True
    else:
        return False
