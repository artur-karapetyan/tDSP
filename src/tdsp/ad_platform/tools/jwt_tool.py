from datetime import datetime, timedelta

import jwt


def generate_jwt(user):
    jwt_payload = {
        "user_id": user.id,
        "username": user.user.username,
        "expiration": str(datetime.utcnow() + timedelta(hours=24)),
        "issued_at_time": str(datetime.utcnow()),
    }
    jwt_token = jwt.encode(jwt_payload, "SECRET_KEY", algorithm="HS256")
    return jwt_token
