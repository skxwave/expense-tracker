from fastapi_users.authentication import BearerTransport

bearer_transport = BearerTransport(tokenUrl="/api/v1/users/auth/jwt/login")
