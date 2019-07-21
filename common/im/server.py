import socketio


# RabbitMQ消息队列连接信息
RABBITMQ = 'amqp://python:rabbitmqpwd@localhost:5672/toutiao'
# 创建RabbitMQ消息队列的管理器对象
manager = socketio.KombuManager(RABBITMQ)

# 创建socketio服务器对象,异步模式采用enentlet协程的方式
sio = socketio.Server(async_mode='eventlet')
# 获取app对象,给协程调用
app = socketio.Middleware(sio)