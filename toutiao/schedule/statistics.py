from common.cache.statistic import UserArticleCountStorage,UserFollowingCountStorage


def fix_thread(count_storage_cls):
    '''
    修复数据工具方法
    :param count_storage_cls: 统计类
    :return: 无
    '''

    # 查询数据库中最新数据
    result = count_storage_cls.db_query()
    # 重设Redis缓存数据
    count_storage_cls.reset(result)


def fix_statistic(flask_app):
    '''
    修正统计数据
    :return:
    '''

    # 开启flask上下文
    with flask_app.app_context():
        # 调用修复工具修复用户文章统计数据
        fix_thread(UserArticleCountStorage)
        # 调用修复工具修复用户被关注的数量
        fix_thread(UserFollowingCountStorage)