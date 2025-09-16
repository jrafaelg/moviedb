from time import time
from typing import Any, Optional, Dict

import jwt
from flask import current_app


def create_jwt_token(action: str = "",
                     sub: Any = None,
                     expires_in: int = 600,
                     extra_data: Optional[Dict[str, str]] = None) -> str:
    """
    Cria um token JWT com os parâmetros fornecidos.

    Args:
        action: A ação para a qual o token está sendo usado (opcional).
        sub: O assunto do token (por exemplo, email do usuário).
        expires_in: O tempo de expiração do token em segundos. Default de 10min
        extra_data: Dicionário com dados adicionais para incluir no payload (opcional).

    Returns:
        O token JWT codificado.
    Raises:
        ValueError: Se o objeto 'sub' não puder ser convertido em string.
    """
    if not hasattr(type(sub), '__str__'): # isinstance(sub, (str, int, float, uuid.UUID)):
        raise ValueError(f"Tipo de objeto 'sub' invalido: {type(sub)}")

    agora = int(time())
    payload = {
        'sub': str(sub),
        'iat': agora,
        'nbf': agora,
        'exp': agora + expires_in,
        'action': action.lower()
    }

    if extra_data is not None and isinstance(extra_data, dict):
        payload['extraData'] = extra_data

    return jwt.encode(payload=payload,
                      key = current_app.config['SECRET_KEY'],
                      algorithm='HS256')

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verifica um token JWT e retorna suas reivindicações.

    Args:
        token: O token JWT a ser verificado.

    Returns:
        Um dicionário contendo as reivindicações do token.
        O dicionário sempre conterá uma chave 'valid' (booleano).
        Se o token for inválido, uma chave 'reason' pode estar presente.
        Se o token for válido, ele conterá 'sub', 'action', 'age' e 'extra_data' (se presentes).
    """

    claims: Dict[str, Any] = {'valid': False}
    try:
        payload = jwt.decode(token,
                             key = current_app.config.get('SECRET_KEY'),
                             algorithms=['HS256'])

        claims.update({'valid': True,
                       'sub': payload.get('sub', None),
                       'action': payload.get('action', None) })

        if 'iat' in payload:
            claims.update({'age': int(time()) - int(payload.get('iat'))})

        if 'extra_data' in payload:
            claims.update({'extraData': payload.get('extra_data')})

    except jwt.ExpiredSignatureError as e:
        current_app.logger.error(f"JWT expired: {e}")
        claims.update({'reason': "expired"})
    except jwt.InvalidTokenError as e:
        current_app.logger.error(f"JWT invalid: {e}")
        claims.update({'reason': "invalid"})
    except jwt.InvalidSignatureError as e:
        current_app.logger.error(f"JWT invalid signature: {e}")
        claims.update({'reason': "bad_signature"})
    except ValueError as e:
        current_app.logger.error(f"ValueError: {e}")
        claims.update({'reason': "valueerror"})

    return claims
