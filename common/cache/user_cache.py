from flask import current_app
from sqlalchemy.orm import load_only
from sqlalchemy.exc import DatabaseError
from rediscluster import StrictRedisCluster
from redis.exceptions import RedisError
from redis import StrictRedis
import json

from common.models.user import User
from common.cache.constants import *


class UserProfileCache:
    '''
    用户资料缓存
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.key = 'user:{}:info'.format(user_id)  # 用户信息在Redis缓存中保存的key

    def save(self):
        '''
        封装缓存回填的工具方法
        :return: user字典 or None
        '''
        # 获取Redis集群对象
        redis_cluster = current_app.redis_cluster  # type:StrictRedis
        # 设置user对象的初始值
        user = None
        # 查询Mysql数据库，获取user对象
        try:
            user = User.query.option(load_only(
                User.name,
                User.mobile,
                User.profile_photo,  # 头像
                User.introduction,  # 简介
                User.certificate  # 认证
            )).filter_by(id=self.user_id).first()
        except DatabaseError as e:
            current_app.logger.error(e)
            raise e
        # 判断是否从Mysql中查询到user
        if user is not None:  # 查到了
            # 转化为字典格式
            user_dict = {
                'name': user.name,
                'mobile': user.mobile,
                'profile_photo': user.profile_photo,
                'introduction': user.introduction,
                'certificate': user.certificate
            }
            # 将用户数据回填到Redis缓存中
            redis_cluster.setex(self.key, UserCachTTL.get_ttl_date(), json.dumps(user_dict))
            # 返回用户数据
            return user_dict
        else:  # 没查到
            # 为了防止缓存雪崩，给Redis中回填一个值代表数据库中没有该用户数据
            redis_cluster.setex(self.key, UserNotFoundCachTTL.get_ttl_date(), -1)
            # 返回空
            return None

    def get(self):
        '''
        获取用户缓存数据
        读取过程：json_str --> json.loads --> user_dict
        储存过程：user --> user_dict --> json.dumps --> json_str
        :return: 用户字典
        '''

        # 获取Redis集群对象
        redis_cluster = current_app.redis_cluster  # type: StrictRedisCluster
        # 获取用户缓存信息
        try:
            cache_data = redis_cluster.get(self.key)  # 用户缓存信息
        except RedisError as e:
            current_app.logger.error(e)
            # 将用户缓存信息设置为空
            cache_data = None
        # 判断用户缓存信息是否为空
        if cache_data is not None:  # 不为空
            # 判断缓存数据是否为-1
            if cache_data == b'-1':  # 说明用户信息在Mysql数据库中不存在
                # 返回None,防止缓存穿透
                return None
            else:  # 有用户信息
                # 将json字符串转化为字典
                user_dict = json.loads(cache_data)
                # 响应用户字典
                return user_dict
        else:  # 缓存中查找不到用户数据
            # 执行封装好的save()方法，查询数据库并进行缓存回填
            user_dict = self.save()
            # 响应
            return user_dict

    def exists(self):
        '''
        用户缓存数据是否存在
        :return: True or False
        '''

        # 获取Redis集群对象
        redis_cluster = current_app.redis_cluster
        # 查询用户缓存数据
        try:
            cache_data = redis_cluster.get(self.key)
        except RedisError as e:
            # 将异常写入日志中
            current_app.logger.error(e)
            # 将用户缓存数据设置为空
            cache_data = None
        # 判断用户缓存数据是否为空
        if cache_data is not None:
            # 判断用户缓存数据是否为-1
            if cache_data == b'-1':
                # 用户数据不存在,返回False
                return False
            else:
                # 用户缓存数据存在,返回True
                return True
        else:
            # 查询Mysql数据库，获取用户数据
            user_dict = self.save()
            # 用户数据是否为空
            if user_dict is not None:
                # 查询到用户数据,返回True
                return True
            else:
                # 未查询到,返回False
                return False

    def clear(self):
        '''
        清除用户缓存数据
        :return: 无
        '''

        # 获取Redis集群对象
        redis_cluster = current_app.redis_cluster  # type:StrictRedis
        # 删除缓存数据
        try:
            redis_cluster.delete(self.key)
        except RedisError as e:
            # 将异常信息写入日志
            current_app.logger.error(e)
            # 上抛异常
            raise e