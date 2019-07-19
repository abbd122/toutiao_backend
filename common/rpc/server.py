# 注意:由于推荐系统服务器会脱离框架独立运行,所以导包时只能从当前目录中导入
import reco_pb2_grpc
import reco_pb2
import time
import grpc

# python3.2新增的模块concurrent
from concurrent.futures import ThreadPoolExecutor


class UserArticleRecommendServicer(reco_pb2_grpc.UserArticleRecommendServicer):
    '''重写reco_pb2_grpc中的服务类'''

    def user_recommend(self, request, context):
        '''
        连接推荐系统,获取推荐文章数据,用于客户端调用
        :param request: Web后端发送的请求对象
        :param context: 错误信息内容
        :return: 推荐文章的响应数据
        '''

        # 获取请求参数
        user_id = request.user_id  # 用户id
        channel_id = request.channel_id  # 频道id
        article_num = request.article_num  # 推荐文章的数量
        timestamp = request.timestamp  # 时间戳

        # 调用推荐系统的方法获取响应数据
        # 伪推荐:手动构建响应对象及参数
        # 构建响应对象
        article_response = reco_pb2.ArticleResponse()
        article_response.exposure = 'exposure info'  # 曝光参数
        article_response.time_stamp = round(time.time() * 1000)  # 时间戳
        # 创建一个空列表,用于存放文章具体数据
        article_list = []
        for i in range(article_num):  # 循环数与请求参数中需要获取的文章数量相同
            # 创建具体推荐文章对象
            article = reco_pb2.Article()
            article.article_id = i + 1  # 文章id, 从１开始
            # 写入埋点数据
            article.track.like = 'like action {}'.format(i + 1)  # 点赞
            article.track.collect = 'collect action {}'.format(i + 1)  # 收藏
            article.track.share = 'share action {}'.format(i + 1)  # 分享
            article.track.repost = 'repost action {}'.format(i + 1)  # 转发
            # 将每个文章对象追加到文章列表中
            article_list.append(article)
        # 扩展相应数据列表recommend
        article_response.recommends.extend(article_list)

        # 返回响应对象
        return article_response


def server():
    '''
    rpc推荐系统服务端的启动函数
    :return: 无
    '''

    # 通过grpc创建服务器对象
    # 通过线程池的方法创建
    server = grpc.server(ThreadPoolExecutor(max_workers=10))

    # 添加服务器和grpc形成关联　　--grpc需要推荐什么类型的数据
    # 参数一servicer : 例如UserArticleRecommendServicer用于推荐文章系统的服务器对象
    # 参数二server : 创建的服务器对象
    reco_pb2_grpc.add_UserArticleRecommendServicer_to_server(UserArticleRecommendServicer(), server)

    # 绑定grpc服务器的ip和端口
    server.add_insecure_port("0.0.0.0:8888")

    # 启动服务器
    server.start()

    # 由于是独立运行,所以需要阻塞服务器
    while True:
        time.sleep(10)


if __name__ == '__main__':
    server()