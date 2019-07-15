from flask import current_app
from sqlalchemy.orm import load_only
import json

from common.models.user import User


class UserProfileCache:
    '''
    用户资料缓存
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.key = 'user:{}:info'.format(user_id)  # 用户信息在Redis缓存中保存的key

    def get(self):
        r = current_app.redis_cluster   # 获取Redis集群对象
        recv_data = r.get(self.key)  # 查询Redis缓存
        if recv_data is not None:  # 判断是否查询到数据
            if recv_data == b'-1':  # 结果如果为-1,说明该用户信息在Mysql数据库中为空,在Redis中设置为-1是为了防止穿透缓存
                return None
            else:  # 不为空则返回用户字典数据
                user_dict = json.loads(recv_data)  # 将接收到的json数据转化为字典格式，使用json可以不需要decode()解码
                return user_dict
        else:  # 如果在Redis缓存中没有查询到数据，再查询Mysql数据
            user = User.query.option(load_only(
                User.name,
                User.mobile,
                User.profile_photo,  # 头像
                User.introduction,  # 简介
                User.certificate  # 认证
            )).filter_by(id=self.user_id).first()
            if user is not None:  # 如果Mysql中查询到用户信息
                r.setex(self.key, 3600*24, json.dumps(user))  # 将用户信息保存到Redis缓存，过期时间乱写的
                user_dict = {  # 将用户信息转化为字典格式
                    'name': user.name,
                    'mobile': user.mobile,
                    'profile_photo': user.profile_photo,
                    'introduction': user.introduction,
                    'certificate': user.certificate
                }
                return user_dict  # 响应用户字典
            else:  # 如果Mysql中没有查询到用户信息
                r.setex(self.key, 3600*24, -1)  # 为了防止缓存穿透，即使没有数据也要在Redis中设置不存在的记录[-1],储存到Redis中的数据会自动转换转化为Bytes类型
                return None