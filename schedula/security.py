from datetime import datetime, timedelta
import secrets
from zoneinfo import ZoneInfo

from fastapi import Request
from schedula.settings import Settings
from schedula.repositories.usuario import obter_usuario_por_token
from pwdlib import PasswordHash


pwd_context = PasswordHash.recommended()
settings = Settings()

def obter_hash_por_senha(password: str):
    return pwd_context.hash(password)

def verificar_senha(senha_simples: str, senha_hashed: str):
    return pwd_context.verify(senha_simples, senha_hashed)

def gerar_token(length: int = 16) -> str:
    return secrets.token_hex(length)

def criar_cookie_token(response, token):
    response.set_cookie(
        key="token",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        httponly=True,
        samesite="Lax",
        )
    return response

def deletar_cookie_token(response):
    response.delete_cookie(key="token")
    return response

def obter_usuario_logado(request: Request):
    try:
        token = request.cookies["token"]
        if token.strip() == "":
            return None
        usuario = obter_usuario_por_token(token)
        return usuario
    except KeyError:
        return None
    