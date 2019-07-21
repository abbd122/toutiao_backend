from server import sio

# 特殊事件
# 连接事件, 与客户端建立好连接后执行
@sio.on('connect')
def connect(sid, environ):
    '''
    :param sid: 唯一标识的客户端id
    :param environ: 客户端与服务端第一次建立连接的握手数据,dict类型
    '''
    print('连接成功: {}'.format(sid))


# 断开连接事件,与客户端断开连接后被执行
@sio.on('disconnect')
def disconnect(sid):
    '''
    :param sid: 唯一标识的客户端id
    '''
    pass

# 非特殊事件
# 自定义事件
@sio.on('my event')
def do_something(sid, data):
    '''
    :param sid: 唯一标识的客户端id
    :param data: 客户端发送给服务器的数据
    '''
    pass


'''
user_sid = None
room_name = None
# 发送消息

# 1.群发
# sio.emit(event='事件名称', data=发送的数据内容)
sio.emit(event='my event', data={'data': 'Hello'})

# 2.单发 -- room=user_sid
# sio.emit(event='事件名称', data=发送的数据内容, room=指定用户的sid)
sio.emit(event='my event', data={'data': 'Hello'}, room=user_sid)

# 3.跳过某个用户 -- skip_sid
sio.emit('my event', {'data': 'Hello'}, room=room_name, skip_sid=user_sid)

# 4.特殊事件简写 -- message
# 原始
sio.emit('message', {'data': 'Hello'}, room=room_name)
# 简写后
sio.send({'data': 'Hello'}, room=room_name)


# 客户端分组(房间)
sid = None

# 1.将sid添加到房间
sio.enter_room(sid, room_name)

# 2.将sid从房间中移除
sio.leave_room(sid, room_name)

# 3.查看sid属于哪个分组(房间)
sio.rooms(sid)
'''