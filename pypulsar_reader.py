import pulsar

# MessageId taken from a previously fetched message

msg_id = msg.message_id()
reader = client.create_reader('my-topic', msg_id)

while True:
    msg = reader.read_next()
    print("Received message '{}' id='{}'".format(msg.data(), msg.message_id()))
