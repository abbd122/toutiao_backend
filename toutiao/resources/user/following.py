from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask import g,current_app
import time

from utils.decorators import *


class FollowingListResource(Resource):

    method_decorators = {
        'post': [login_reqired],
        'get': [login_reqired]
    }

    def post(self):

        reqparser = RequestParser()
        # 获取被关注用户id
        reqparser.add_argument('token', type=int, location='json', required=True)
        target = reqparser.parse_args().target

        # 省略数据库操作,只进行消息推送逻辑
        # 构建推送数据
        send_data = {
            'user_id': g.user_id,
            'user_name': '小小',
            'user_photo': 'photo...',
            'timestamp': round(time.time())
        }
        # 推送消息
        current_app.sio.emit('following', send_data, room=str(target))

        return {'target': target}, 201
