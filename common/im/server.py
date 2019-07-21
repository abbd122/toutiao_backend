import socketio


# 创建socketio服务器对象,异步模式采用enentlet协程的方式
sio = socketio.Server(async_mode='eventlet')
# 获取app对象,给协程调用
app = socketio.Middleware(sio)