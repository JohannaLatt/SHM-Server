import pika
from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_KINECT_KEYS
from Server.utils.enums import MSG_TO_MIRROR_KEYS
from Server import module_manager as ModuleManager
import configparser
import queue


# Callback for consuming incoming messages from the Mirror
def consume_mirror_message(ch, method, properties, body):
    # print(" [info] %r:%r" % (method.routing_key, body))
    # Call module callbacks depending on incoming message
    if method.routing_key == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
        for module in ModuleManager.modules:
            module.mirror_started()
    else:
        print('[Messaging][warning] Received unknown key {}'.format(method.routing_key))


# Callback for consuming incoming messages from the Kinect
def consume_kinect_message(ch, method, properties, body):
    # Call module callbacks depending on incoming message
    if method.routing_key == MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name:
        for module in ModuleManager.modules:
            module.tracking_started()
    elif method.routing_key == MSG_FROM_KINECT_KEYS.TRACKING_DATA.name:
        for module in ModuleManager.modules:
            module.tracking_data(body)
    elif method.routing_key == MSG_FROM_KINECT_KEYS.TRACKING_LOST.name:
        for module in ModuleManager.modules:
            module.tracking_lost()
    else:
        print('[Messaging][warning] Received unknown key {}'.format(method.routing_key))


def init():
    # Create a local messaging connection
    Config = configparser.ConfigParser()
    Config.read('./config/mirror_config.ini')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=Config.get('General', 'messaging_ip')))

    global __channel_consuming
    global __channel_sending
    __channel_consuming = connection.channel()
    __channel_sending = connection.channel()


def initiate_message_consuming():
    if __channel_consuming is None:
        init()

    __initiate_messaging_from_outside('from-mirror', MSG_FROM_MIRROR_KEYS, consume_mirror_message)
    __initiate_messaging_from_outside('from-kinect', MSG_FROM_KINECT_KEYS, consume_kinect_message)


def __initiate_messaging_from_outside(name, keys, consume_callback):
    # Create an exchange for the messages of the exchange with 'name'
    __channel_consuming.exchange_declare(exchange=name, exchange_type='direct')

    # Declare a __queue to be used (random name will be used)
    result = __channel_consuming.queue_declare(exclusive=True)
    queue_name = result.method.queue

    # Listen to the messages with the given keys
    for msg_keys in keys:
        __channel_consuming.queue_bind(exchange=name,
                           queue=queue_name,
                           routing_key=msg_keys.name)

    __channel_consuming.basic_consume(consume_callback,
                          queue=queue_name,
                          no_ack=True)


def initiate_messaging_to_mirror():
    if __channel_sending is None:
        init()

    # Save the queue
    global __queue
    __queue = queue.Queue()

    # Create an exchange for the mirror-messages - type is direct so we can distinguish the different messages
    __channel_sending.exchange_declare(exchange='to-mirror', exchange_type='direct')


def start_consuming():
    try:
        __channel_consuming.start_consuming()
    except pika.exceptions.ConnectionClosed as cce:
        print('[Messaging][error] %r' % cce)


# Threadsafe sending of messages
def start_sending():
    while True:
        item = __queue.get()
        if item is None:
            continue
        try:
            __channel_sending.basic_publish(exchange='to-mirror',
                              routing_key=item['key'],
                              body=item['body'])
            #print("[info] Sent {}: {}".format(item['key'], item['body'][0:50]))
        except pika.exceptions.ConnectionClosed as cce:
            print('[Messaging - error] %r' % cce)
        __queue.task_done()


def send_message(key, body):
    if __channel_sending is None:
        init()

    if key not in MSG_TO_MIRROR_KEYS.__members__:
        print("[Messaging][error] %r is not a valid message key to send to the mirror" % key)
    else:
        __queue.put({'key': key, 'body': body})
