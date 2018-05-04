from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_KINECT_KEYS
from Server.utils.enums import MSG_TO_MIRROR_KEYS

from Server import module_manager as ModuleManager

from amqpstorm import Connection

import configparser
import queue


# The format in which messages are shared accross the service
class MirrorMessage:
    def __init__(self, key, body):
        self.key = key
        self.body = body


# The queue that saves incoming messages
mirror_msg_queue = queue.Queue()


# Callback for consuming incoming messages from the Mirror
def consume_mirror_message(message):
    if message.method['routing_key'] == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
        mirror_msg_queue.put(MirrorMessage(MSG_FROM_MIRROR_KEYS.MIRROR_READY.name, ''))
    else:
        print('[Messaging][warning] Received unknown key {}'.format(message.method['routing_key']))


# Callback for consuming incoming messages from the Kinect
def consume_kinect_message(message):
    # Call module callbacks depending on incoming message
    if message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name:
        mirror_msg_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name, ''))
    elif message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_DATA.name:
        mirror_msg_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_DATA.name, message.body))
    elif message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_LOST.name:
        mirror_msg_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_LOST.name, ''))
    else:
        print('[Messaging][warning] Received unknown key {}'.format(message.method['routing_key']))


def init():
    # Create a local messaging connection
    Config = configparser.ConfigParser()
    Config.read('./config/mirror_config.ini')
    connection = Connection(Config.get('General', 'messaging_ip'), 'guest', 'guest')

    global __channel_consuming
    global __channel_sending
    __channel_consuming = connection.channel()
    __channel_sending = connection.channel()

    _initiate_messaging_to_mirror()
    _initiate_message_consuming()


def _initiate_messaging_to_mirror():
    if __channel_sending is None:
        init()

    # Save the queue
    global __queue
    __queue = queue.Queue()

    # Create an exchange for the mirror-messages - type is direct so we can distinguish the different messages
    __channel_sending.exchange.declare(exchange='to-mirror', exchange_type='direct')


def _initiate_message_consuming():
    if __channel_consuming is None:
        init()

    __initiate_messaging_from_outside('from-mirror', MSG_FROM_MIRROR_KEYS, consume_mirror_message)
    __initiate_messaging_from_outside('from-kinect', MSG_FROM_KINECT_KEYS, consume_kinect_message)


def __initiate_messaging_from_outside(name, keys, consume_callback):
    # Create an exchange for the messages of the exchange with 'name'
    __channel_consuming.exchange.declare(exchange=name, exchange_type='direct')

    # Declare a __queue to be used (random name will be used)
    result = __channel_consuming.queue.declare(exclusive=True)
    queue_name = result['queue']

    # Listen to the messages with the given keys
    for msg_keys in keys:
        __channel_consuming.queue.bind(exchange=name,
                           queue=queue_name,
                           routing_key=msg_keys.name)

    __channel_consuming.basic.consume(consume_callback,
                          queue=queue_name,
                          no_ack=True)


def start_consuming():
    __channel_consuming.start_consuming()


# Threadsafe sending of messages
def start_sending():
    while True:
        item = __queue.get()
        if item is None:
            continue
        __channel_sending.basic.publish(exchange='to-mirror',
                          routing_key=item.key,
                          body=item.body)
        # print("[info] Sent {}: {}".format(item['key'], item['body'][0:50]))
        __queue.task_done()


def send_message(key, body):
    if __channel_sending is None:
        init()

    if key not in MSG_TO_MIRROR_KEYS.__members__:
        print("[Messaging][error] %r is not a valid message key to send to the mirror" % key)
    else:
        if key == MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name:
            __queue.queue.clear()
        __queue.put(MirrorMessage(key, body))
