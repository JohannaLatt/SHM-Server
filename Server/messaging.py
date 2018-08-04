from Server.utils.enums import MSG_FROM_MIRROR_KEYS
from Server.utils.enums import MSG_FROM_KINECT_KEYS
from Server.utils.enums import MSG_TO_MIRROR_KEYS

from amqpstorm import Connection

import configparser
import queue
import json


# The format in which messages are shared accross the service
class MirrorMessage:
    def __init__(self, key, body):
        self.key = key
        self.body = body


class Messaging:

    def __init__(self):
        # Queue to save all incoming messages
        self.incoming_msgs_queue = queue.Queue()

        # Create a messaging connection
        Config = configparser.ConfigParser()
        Config.read('./config/mirror_config.ini')
        connection = Connection(Config.get('General', 'messaging_ip'), 'guest', 'guest')

        global __channel_consuming
        global __channel_sending
        __channel_consuming = connection.channel()
        __channel_sending = connection.channel()

        self._initiate_messaging_to_mirror()
        self._initiate_message_consuming()

    # Callback for consuming incoming messages from the Mirror
    def consume_mirror_message(self, message):
        if message.method['routing_key'] == MSG_FROM_MIRROR_KEYS.MIRROR_READY.name:
            self.incoming_msgs_queue.put(MirrorMessage(MSG_FROM_MIRROR_KEYS.MIRROR_READY.name, ''))
        else:
            print('[Messaging][warning] Received unknown key {}'.format(message.method['routing_key']))

    # Callback for consuming incoming messages from the Kinect
    def consume_kinect_message(self, message):
        if message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name:
            self.incoming_msgs_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_STARTED.name, ''))
        elif message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_DATA.name:
            self.incoming_msgs_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_DATA.name, message.body))
        elif message.method['routing_key'] == MSG_FROM_KINECT_KEYS.TRACKING_LOST.name:
            self.incoming_msgs_queue.put(MirrorMessage(MSG_FROM_KINECT_KEYS.TRACKING_LOST.name, ''))
        else:
            print('[Messaging][warning] Received unknown key {}'.format(message.method['routing_key']))

    def consume_internal_message(self, key):
        self.incoming_msgs_queue.put(MirrorMessage(key, ''))

    def _initiate_messaging_to_mirror(self):
        # Save the queue
        self.outgoing_msgs_queue = queue.Queue()

        # Create an exchange for the mirror-messages - type is direct so we can distinguish the different messages
        __channel_sending.exchange.declare(exchange='to-mirror', exchange_type='direct')

    def _initiate_message_consuming(self):
        self.__initiate_messaging_from_outside('from-mirror', MSG_FROM_MIRROR_KEYS, self.consume_mirror_message)
        self.__initiate_messaging_from_outside('from-kinect-skeleton', MSG_FROM_KINECT_KEYS, self.consume_kinect_message)

    def __initiate_messaging_from_outside(self, name, keys, consume_callback):
        # Create an exchange for the messages of the exchange with 'name'
        __channel_consuming.exchange.declare(exchange=name, exchange_type='direct')

        # Declare a outgoing_msgs_queue to be used (random name will be used)
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

    def start_consuming(self):
        __channel_consuming.start_consuming()



    ''' Threadsafe sending of messages '''
    def start_sending(self):
        while True:
            item = self.outgoing_msgs_queue.get()
            if item is None:
                continue
            __channel_sending.basic.publish(exchange='to-mirror',
                              routing_key=item.key,
                              body=item.body)
            # print("[info] Sent {}: {}".format(item['key'], item['body'][0:50]))
            self.outgoing_msgs_queue.task_done()

    def send_message(self, key, body):
        if key not in MSG_TO_MIRROR_KEYS.__members__:
            print("[Messaging][error] %r is not a valid message key to send to the mirror" % key)
        else:
            if key == MSG_TO_MIRROR_KEYS.CLEAR_SKELETON.name:
                self.outgoing_msgs_queue.queue.clear()
            self.outgoing_msgs_queue.put(MirrorMessage(key, body))



    ''' HELPERS '''
    def send_text_to_mirror(self, text, id="", color=(1, 1, 1, 1), halign="center", position={"x":0,"y":0}, font_size=30, fade_in=0.5, stay=10000, fade_out=1):
        self.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
            json.dumps({
             "text": text,
             "id": id,
             "position": position,
             "halign": halign,
             "font_size": font_size,
             "color": color,
             "animation": {
                 "fade_in": fade_in,
                 "stay": stay,
                 "fade_out": fade_out}
             }))

    def hide_text_message(self, id):
        self.send_message(MSG_TO_MIRROR_KEYS.TEXT.name,
            json.dumps({
                "text": "",
                "id": id,
                "animation": {
                    "stay": 0,
                    "fade_out": 0
                }
            }))
