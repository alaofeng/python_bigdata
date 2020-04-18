
# 导入
import pulsar

#创建客户端
client = pulsar.Client('pulsar://localhost:6650')

'''
client参数列表如下：

service_url,
authentication=None,
operation_timeout_seconds=30,
io_threads=1,
message_listener_threads=1,
concurrent_lookup_requests=50000,
log_conf_file_path=None,
use_tls=False,
tls_trust_certs_file_path=None,
tls_allow_insecure_connection=False,
tls_validate_hostname=False,
'''

consumer = client.subscribe('my-topic2','my-subscription')
"""
   第一个参数topic接受如下几种形式
   1. string, topic名
   2. list,多个topic名
   3. 正则表达式，例如 re.compile('topic-.*')
"""
while True:
	# 开始接收消息，有一个timeout参数可以设置，单位是毫秒 timeout_millis=None

	msg = consumer.receive()

	try:
	  print("Received message '{}' id='{}'".format(msg.data(),msg.message_id()))

	  # 发送接收成功的ack
	  consumer.acknowledge(msg)
	except:
	  # 发送接收失败的ack
	  consumer.negative_acknowledge(msg)
client.close()
