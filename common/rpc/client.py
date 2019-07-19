import reco_pb2
import reco_pb2_grpc
import grpc


def feed_article(stub):
    '''
    构建请求参数,获取推荐数据
    :param stub: 助手
    :return: 推荐数据
    '''

    # 创建请求对象
    request = reco_pb2.UserRequest()
    # 构建请求数据
    request.user_id = '1'  # 用户id
    request.channel_id = 1  # 频道id
    request.article_num = 10  # 需要获取的文章数量
    request.timestamp = 12345678  # 推荐时间戳

    # 使用助手调用服务端方法获取推荐数据
    response = stub.user_recommend(request)
    print(response)

    # 返回推荐数据
    return response


def client():
    '''
    客户端启动函数,连接服务端调用feed_article方法获取推荐数据
    :return: 无
    '''

    # 创建连接
    with grpc.insecure_channel('192.168.88.131:8888') as channel:
        # 生成一个sub助手
        stub = reco_pb2_grpc.UserArticleRecommendStub(channel)
        # 通过助手调用feed_article()函数获取推荐数据
        feed_article(stub)


if __name__ == '__main__':
    client()
