import pika
from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server import module_manager as ModuleManager


# Callback for consuming incoming messages
def consume_mirror_message(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # Call module callbacks depending on incoming message
    if method.routing_key == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
        for module in ModuleManager.modules:
            module.mirror_started()
    elif method.routing_key == MSG_FROM_MIRROR_KEYS.MIRROR_TRACKING_DATA.name:
        for module in ModuleManager.modules:
            module.mirror_tracking_data(body)
    else:
        print('else')


def init():
    # Create a local messaging connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    global __channel
    __channel = connection.channel()


def initiate_messaging_from_mirror():
    if __channel is None:
        init()

    # Create an exchange for the mirror-messages
    __channel.exchange_declare(exchange='from-mirror', exchange_type='direct')

    # Declare a queue to be used (random name will be used)
    result = __channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    # Listen to mirror messages
    for msg_keys in MSG_FROM_MIRROR_KEYS:
        __channel.queue_bind(exchange='from-mirror',
                           queue=queue_name,
                           routing_key=msg_keys.name)

    __channel.basic_consume(consume_mirror_message,
                          queue=queue_name,
                          no_ack=True)


def initiate_messaging_to_mirror():
    if __channel is None:
        init()

    # Create an exchange for the mirror-messages - type is direct so we can distinguish the different messages
    __channel.exchange_declare(exchange='to-mirror', exchange_type='direct')


def send_message(key, body):
    __channel.basic_publish(exchange='to-mirror',
                    routing_key=key,
                    body=body)

def start_consuming():
    __channel.start_consuming()
