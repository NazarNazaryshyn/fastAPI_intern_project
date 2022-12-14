import jwt
from src.config import settings
from fastapi import HTTPException, status

def set_up():
    config = {
        "DOMAIN": settings.DOMAIN,
        "API_AUDIENCE": settings.API_AUDIENCE,
        "ISSUER": settings.ISSUER,
        "ALGORITHMS": settings.ALGORITHMS
    }

    return config


class VerifyToken():
    def __init__(self, token):
        self.token = token
        self.config = set_up()

        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self) -> str:
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.__str__)
        except jwt.exceptions.DecodeError as error:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.__str__)

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return payload