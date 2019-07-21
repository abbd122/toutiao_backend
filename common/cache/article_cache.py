from flask import current_app
from redis import RedisError,StrictRedis
from sqlalchemy.exc import DatabaseError
import json

from models.news import Article
from cache.constants import ArticleCachTTL,ArticleNotFoundCachTTL


class ArticleInfoCache:
    '''文章缓存数据'''

    def __init__(self, article_id):
        self.article_id = article_id
        self.key = 'article:{}:info'.format(article_id)

    def save(self):
        '''
        缓存回填
        :return: article_dict 文章缓存数据字典
        '''

        # 创建Redis集群对象
        redis_cluster = current_app.redis_cluster  # type:StrictRedis
        # 查询Mysql数据库,获取文章内容
        try:
            article_content = Article.query.get(self.article_id)
        except DatabaseError as e:
            current_app.logger.error(e)
            raise e
        if article_content is not None:
            # 构建字典
            article_dict = {
                'content': article_content.content
            }
            redis_cluster.setex(self.key, ArticleCachTTL.get_ttl_date(), article_dict)
            return article_dict
        else:
            redis_cluster.setex(self.key, ArticleNotFoundCachTTL.get_ttl_date(), -1)
            return None

    def get(self):
        '''
        获取文章数据缓存
        :return: 文章数据
        '''

        # 获取redis集群对象
        redis_cluster = current_app.redis_cluster
        # 获取文章具体内容
        try:
            cache_data = redis_cluster.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            return None
        if cache_data is not None:
            if cache_data == b'-1':
                return None
            else:
                article_dict = json.loads(cache_data)
                return article_dict
        else:
            article_dict = self.save()
            return article_dict

