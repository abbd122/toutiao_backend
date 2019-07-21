import random


class BaseCachTTL(object):
    '''设置Redis缓存的过期时长的基类'''

    # 设置基础过期时长，2小时
    TTL = 2 * 60 * 60
    # 最大随机时长,10分钟
    MAX_DATE = 10 * 60

    @classmethod
    def get_ttl_date(cls):
        '''
        获取过期时长
        :return: 过期时长
        '''
        return cls.TTL + random.randrange(0, cls.MAX_DATE)


class UserCachTTL(BaseCachTTL):
    '''用户信息的缓存过期时长'''

    # 与基类一致
    pass


class UserNotFoundCachTTL(BaseCachTTL):
    '''用户未找到的缓存过期时长'''

    # 重写基础过期时长,1小时
    TTL = 60 * 60
    # 重写随机最大过期时长,5分钟
    MAX_DATE = 5 * 60


class ArticleCachTTL(BaseCachTTL):
    '''文章数据过期时长'''

    pass


class ArticleNotFoundCachTTL(BaseCachTTL):
    '''文章缓存未找到的过期时长'''

    TTL = 60 * 60
    MAX_DATE = 5 * 60