import pika
from enum import Enum
from . import modules as Modules


class MIRROR_KEY(Enum):
    MIRROR_READY = 1
    MIRROR_TRACKING_STARTED = 2
    MIRROR_TRACKING_DATA = 3
    MIRROR_TRACKING_LOST = 4


# Callback for consuming incoming messages
def consume_mirror_message(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # Call module callbacks depending on incoming message
    if method.routing_key == MIRROR_KEY.MIRROR_READY.name:
        for module in Modules.modules:
            module.mirror_started()
    elif method.routing_key == MIRROR_KEY.MIRROR_TRACKING_DATA.name:
        for module in Modules.modules:
            module.mirror_tracking_data(body)
    else:
        print('else')


def initiate_messaging():
    # Create a local messaging connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Create an exchange for the mirror-messages
    channel.exchange_declare(exchange='mirror', exchange_type='direct')

    # Declare a queue to be used (random name will be used)
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    # Listen to mirror messages
    for msg_keys in MIRROR_KEY:
        channel.queue_bind(exchange='mirror',
                           queue=queue_name,
                           routing_key=msg_keys.name)

    channel.basic_consume(consume_mirror_message,
                          queue=queue_name,
                          no_ack=True)

    channel.start_consuming()
