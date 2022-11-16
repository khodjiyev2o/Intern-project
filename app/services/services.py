from os import getenv
from jwt import encode, decode, PyJWKClient
from fastapi import HTTPException


def create_token(data: dict) -> str:
    try:
        return encode(data, getenv('SECRET_KEY'), algorithm='HS256')
    except:
        raise HTTPException(404, 'token creation error')


def read_token(Token: str, TokenType: str) -> str:
    try:
        if TokenType == 'app':
            data = decode(Token, getenv('SECRET_KEY'), ['HS256'])
            email = data['email']
            return email
        elif TokenType == 'auth0':
            jwks_client = PyJWKClient(getenv('AUTH0_PUBLIC_URL'))
            signing_key = jwks_client.get_signing_key_from_jwt(Token)
            data = decode(
                Token,
                signing_key.key,
                algorithms=['RS256'],
                audience=getenv('AUTH0_AUDIENCE'))
            email = data['user_email']
            return email
        else:
            raise Exception
    except:
        raise HTTPException(404, 'token validation error')
