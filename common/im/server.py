import socketio
import eventlet
import sys
import eventlet.wsgi


# 将系统中所有io标准函数转换为eventlet同名函数,遇到阻塞eventlet会自动切换协程
eventlet.monkey_patch()

# 创建socketio服务器,异步模式采用enentlet协程的方式
sio = socketio.Server(async_mode='eventlet')
# 获取app对象,给协程调用
app = socketio.Middleware(sio)
# 设置动态端口
if len(sys.argv) < 2:
    print('useage: python server.py [port]')
    exit(1)
port = int(sys.argv[1])
# 设置socket服务器监听的ip和端口
SOCKET_ADDRESS = ('', port)
# 设置事件监听
socket = eventlet.listen(SOCKET_ADDRESS)
# 绑定sio服务器和协程套接字,通过协程的异步模式将服务器运行在制定的ip和端口上
eventlet.wsgi.server(socket, app)


