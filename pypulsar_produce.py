import pulsar

client = pulsar.Client('pulsar://localhost:6650')


# 创建topic
producer = client.create_producer('my-topic2')

# 发送数据
for i in range(10):
    producer.send(('Hello-%d' % i).encode('utf-8'))

client.close()
