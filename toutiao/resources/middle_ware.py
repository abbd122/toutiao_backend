from flask import request,g

from common.utils.jwt_util import *


def jwt_authorization():
    g.user_id = None
    g.is_refresh = False

    header_token = request.headers.get('Authorization')
    if header_token and header_token.startswith('Bearer '):
        token = header_token[7:]
        payload = verify_jwt(token)
        if payload:
            g.user_id = payload.get('user_id')
            g.is_refresh = payload.get('is_refresh', False)