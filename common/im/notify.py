from server import sio
from utils.jwt_util import verify_jwt

import time
from werkzeug.wrappers import Request  # 请求对象request的父类


def get_target_userid(token):
    '''
    获取被关注用户的id
    :param token: 被关注用户访问携带的token
    :return: 被关注用户的id
    '''

    # jwt秘钥
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    # 调用工具函数获取token中的payload
    payload = verify_jwt(token, secret=JWT_SECRET)
    if payload is not None:
        # 返回被关注用户的id
        return payload.get('user_id')
    else:
        return None


@sio.on('connect')
def connect(sid, environ):
    '''
    用户上线后触发,获取到被关注用户id,并添加到用户分组中接收推送消息
    :param sid: 用户唯一标识
    :param environ: 首次连接的握手数据
    :return: 无
    '''

    # 获取请求对象
    request = Request(environ)
    # 获取查询参数token
    token = request.args.get('token')
    # 获取被关注用户id
    target_user_id = get_target_userid(token)
    if target_user_id is not None:
        # 将该客户端添加到用户分组中
        sio.enter_room(sid, room=str(target_user_id))


@sio.on('disconnect')
def disconnect(sid):
    '''
    退出将该用户从所有房间中移除
    :param sid: 用户唯一标识
    :return: 无
    '''

    # 获取该用户的所有房间
    rooms = sio.rooms(sid)
    # 遍历并依次移除
    for room in rooms:
        sio.leave_room(sid, room=room)
