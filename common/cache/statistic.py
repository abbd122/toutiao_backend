from flask import current_app
from redis.exceptions import RedisError


class CountStorageBase(object):
    '''用户统计数据储存父类'''

    # 默认类属性：Redis用户数据的key
    key = ''

    @classmethod
    def get(cls, user_id):
        '''
        获取指定用户的权重值
        :param user_id: 用户id
        :return: 用户权重值 or 0
        '''

        # 获取缓存数据
        try:
            # 主服务器获取数据
            result = current_app.redis_master.zscore(cls.key, user_id)
        except RedisError as e:
            # 将异常保存到日志中
            current_app.logger.error(e)
            # 从服务器获取数据
            result = current_app.redis_slave.zscore(cls.key, user_id)
        # 判断是否获取到值
        if result is not None:
            # 转化为整型并返回
            return int(result)
        else:
            # 返回0
            return 0

    @classmethod
    def incr(cls, user_id, increment=1):
        '''
        给指定用户的统计数据进行累加
        :param user_id: 用户id
        :param increment: 累加的增量
        :return: 无
        '''

        current_app.redis_master.zincrby(cls.key, user_id, increment)


class UserArticleCountStorage(CountStorageBase):
    '''用户文章统计'''

    key = 'count:user:arts'


class UserFollowingCountStorage(CountStorageBase):
    '''用户被关注的数量'''

    key = 'count:user:followings'