"""Autenticación real: login con hash bcrypt y sesión JWT (RNF-02.1, RNF-02.3, RNF-02.4)."""
import os
import time

import jwt
from fastapi import Header, HTTPException, Depends
import bcrypt
from pydantic import BaseModel

from db import SessionLocal, Usuario

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-cambiar-en-produccion")
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "60"))  # 60 min de sesión

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class LoginIn(BaseModel):
    email: str
    password: str


def crear_token(usuario: Usuario) -> str:
    payload = {
        "sub": usuario.email,
        "rol": usuario.rol,
        "cooperativaId": usuario.cooperativaId,
        "exp": int(time.time()) + JWT_EXP_MIN * 60,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def usuario_actual(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    try:
        payload = jwt.decode(authorization[7:], JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sesión expirada")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
