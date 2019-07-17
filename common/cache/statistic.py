from flask import current_app
from redis.exceptions import RedisError
from sqlalchemy import func
from models import db

from common.models.news import Article
from common.models.user import Relation


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

    @classmethod
    def reset(cls, db_query_ret):
        '''
        定时修复缓存数据
        :param db_query_ret: (date_id, count) Mysql数据库查询出的最新id和对应的统计数量
        :return: 无
        '''

        # 创建Redis管道对象
        pl = current_app.redis_master.pipeline()
        # 删除Redis中的用户缓存记录
        pl.delete(cls.key)
        redis_data = []
        # 获取Mysql中查询出的最新数据
        for date_id, count in db_query_ret:
            # 追加到列表中
            redis_data.append(count)
            redis_data.append(date_id)
        # redis_data = [count1, date_id_1, count2, date_id_2, ...]
        # 调用管道对象储存最新数据到Redis
        pl.zadd(cls.key, *redis_data)
        # 执行管道对象
        pl.execute()


class UserArticleCountStorage(CountStorageBase):
    '''用户文章统计'''

    key = 'count:user:arts'

    # 静态方法
    @staticmethod
    def db_query():
        '''
        查询数据库中最新文章数据
        :return: 最新文章统计数据和对应的user_id
        '''
        # 查询出所有最新审核通过的文章数量及其所对应的user_id,按用户进行分组
        result = db.session.query(Article.user_id, func.count(Article.id))\
            .filter(Article.status == Article.STATUS.APPROVED).group_by(Article.user_id).all()
        return result


class UserFollowingCountStorage(CountStorageBase):
    '''用户被关注的数量'''

    key = 'count:user:followings'

    @staticmethod
    def db_query():
        # 查询出最新的用户粉丝数
        result = db.session.query(Relation.user_id, func.count(Relation.target_user_id))\
            .filter(Relation.relation == Relation.RELATION.FOLLOW).group_by(Relation.user_id).all()
        return result