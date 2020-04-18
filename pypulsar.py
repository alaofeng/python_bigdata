import pulsar

client = pulsar.Client('pulsar://localhost:6650')
producer = client.create_producer('my-topic2')
for i in range(10):
    producer.send(('Hello-%d' % i).encode('utf-8'))
client.close()



import pulsar
client = pulsar.Client('pulsar://localhost:6650')
consumer = client.subscribe('my-topic2','my-subscription')
while True:
	msg = consumer.receive()
	try:
	  print("Received message '{}' id='{}'".format(msg.data(),msg.message_id()))
	  consumer.acknowledge(msg)
	except:
	  consumer.negative_acknowledge(msg)
client.close()
