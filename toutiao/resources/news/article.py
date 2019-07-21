from flask_restful import Resource
from flask import current_app,g
from flask_restful.reqparse import RequestParser
from concurrent.futures import ThreadPoolExecutor
import time
import grpc
from flask_restful import inputs

from common.rpc import reco_pb2,reco_pb2_grpc  # 用于flask后端启动的导包路径
from common.cache.article_cache import ArticleInfoCache


class ArticleListResource(Resource):
    '''文章推荐系统'''

    def _feed_articles(self, channel_id, article_num, timestamp):
        '''
        获取推荐文章数据
        :param channel_id: 频道id
        :param article_num:  推荐文章数量
        :param timestamp:  时间戳
        :return: 推荐文章数据
        '''

        # 获取连接对象
        rpc_reco = current_app.rpc_reco
        # 获取助手
        stub = reco_pb2_grpc.UserArticleRecommendStub(rpc_reco)
        # 创建请求对象
        request = reco_pb2.UserRequest()
        # 构建请求参数
        request.user_id = str(g.user_id) if g.user_id else 'anony'
        request.channel_id = channel_id
        request.article_num = article_num
        request.timestamp = timestamp
        # 通过助手调用服务端方法获取推荐数据
        reco_data = stub.user_recommend(request)
        # 返回文章列表数据,时间戳
        return reco_data.recommends, reco_data.time_stamp

    def get(self):
        '''
        获取推荐文章数据的接口函数
        :return: 推荐文章数据响应
        '''

        # 构建解析对象
        request_parse = RequestParser()
        # 接收校验参数
        channel_id = request_parse.add_argument('channel_id', type=int, required=True, location='args')
        timestamp = request_parse.add_argument('timestamp', type=inputs.positive, required=True, location='args')
        # 获取校验后的参数
        result = request_parse.parse_args()
        channel_id = result.channel_id
        timestamp = result.timestamp
        # 推荐文章数量:每页显示个数
        article_num = 10

        try:
            feed_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        except Exception:
            return {'message': 'timestamp param error'}, 400

        # 创建空列表,用于存放响应数据
        results = []
        # 调用内置方法,获取推荐数据
        article_list, time_stamp = self._feed_articles(channel_id, article_num, timestamp)
        # 遍历推荐文章列表
        for article in article_list:
            article_id = article.article_id
            # 根据文章id从缓存工具类中获取文章数据
            article_data = ArticleInfoCache(article_id).get()
            # 向响应字典中新增数据
            if article_data:
                article_data['pubdate'] = feed_time
                article_data['track'] = {
                    'like': article.track.like,
                    'collect': article.track.collect,
                    'share': article.track.share,
                    'repost': article.track.repost
                }
                results.append(article_data)
        # 返回响应
        return {'pre_timestamp': time_stamp, 'results': results}