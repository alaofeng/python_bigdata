from enum import Enum
import pulsar
from pulsar.schema import *

# 枚举
class Color(Enum):
    red = 1
    green = 2
    blue = 3

class MySubRecord(Record):
    x = Integer()
    y = Long()
    z = String()

class Example(Record):
    a = String()
    b = Integer()
    c = Boolean()
    d = Color
    arr = Array(String())
    m = Map(String())
    sub = MySubRecord()

client = pulsar.Client('pulsar://localhost:6650')


producer = client.create_producer(
                    topic='topic-schema',
                    schema=AvroSchema(Example) )

producer.send(Example(a='Hello', b=1, c=True, d=Color.blue, arr=[], m={}, sub=MySubRecord(x=1, y=100, z='subrecorder')))


consumer = client.subscribe(
                  topic='topic-schema',
                  subscription_name='a topic with schema',
                  schema=AvroSchema(Example))

while True:
    msg = consumer.receive()
    ex = msg.value()
    try:
        print("Received message a={} b={} c={}".format(ex.a, ex.b, ex.c))
        # Acknowledge successful processing of the message
        consumer.acknowledge(msg)
    except:
        # Message failed to be processed
        consumer.negative_acknowledge(msg)