from server import sio
import time


"""
需求：
1.当客户端连接sio服务器成功后，im主动发送一条消息给客户端
2.当客户端发送消息给sio服务器，调用（RPC）AI系统智能回复一条消息

数据格式：
{
    "msg": "内容",
    "timestamp": "时间戳"
}

前后端自定义消息事件类型字符串: message
"""


@sio.on('connect')
def connect(sid, environ):
    '''
    1.当客户端连接sio服务器成功后，im主动发送一条消息给客户端
    :param sid: 唯一用户标识
    :param environ: 首次连接的握手数据,dict类型
    :return: 连接成功信息
    '''

    # 应答数据
    reply_data = {
        'msg': '连接成功:{}'.format(sid),
        'timestamp': round(time.time())
    }
    # 使用sio服务器对象发送数据
    # sio.emit('message', reply_data, room=sid)
    sio.send(reply_data, room=sid)


@sio.on('message')
def ai_reply(sid, data):
    '''
    2.当客户端发送消息给sio服务器，调用（RPC）AI系统智能回复一条消息
    :param sid: 唯一用户标识
    :param data: 客户端发送的数据
    :return: AI系统回复的消息
    '''

    # 模拟AI系统应答数据
    reply_data = {
        'msg': '你好,我是小智,已收到你的咨询:{}'.format(data),
        'timestamp': round(time.time())
    }
    # 发送
    sio.send(reply_data, room=sid)