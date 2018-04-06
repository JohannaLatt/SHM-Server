from flask import Flask
import pika
import configparser
import importlib
from enum import Enum

app = Flask(__name__)

# Create a local messaging connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Create an exchange for the mirror-messages
channel.exchange_declare(exchange='mirror', exchange_type='direct')

# Declare a queue to be used (random name will be used)
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue


# Listen to mirror messages
class MIRROR_KEY(Enum):
    MIRROR_READY = 1
    MIRROR_TRACKING_STARTED = 2
    MIRROR_TRACKING_DATA = 3
    MIRROR_TRACKING_LOST = 4


for msg_keys in MIRROR_KEY:
    channel.queue_bind(exchange='mirror',
                       queue=queue_name,
                       routing_key=msg_keys.name)


# Instantiate all modules from the config
modules = []

Config = configparser.ConfigParser()
Config.read('./config/mirror_config.ini')
module_config_names = Config.get('General', 'module_names').split(',')
for module_config_name in module_config_names:
    module_path = Config.get(module_config_name, 'path_name')
    module_class = Config.get(module_config_name, 'class_name')
    #module = importlib.import_module('formmodules."+my_module)

    #module = importlib.import_module(module_path)
    #class_ = getattr(module, module_class)
    #instance = class_()
    #modules.append(instance)

    #loader = importlib.machinery.SourceFileLoader(module_class, module_path)
    #mod = types.ModuleType(loader.name)
    #loader.exec_module(mod)
    #modules.append(mod)


# Consume incoming messages
def consume_mirror_message(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))
    # Call module callbacks depending on incoming message
    if method.routing_key == MIRROR_KEY.MIRROR_READY.name:
        print('mirror started')
        for module in modules:
            module.mirror_started()
    elif method.routing_key == MIRROR_KEY.MIRROR_TRACKING_DATA.name:
        print('mirror tracking %x', body)
        for module in modules:
            module.mirror_tracking_data(body)
    else:
        print('else')


channel.basic_consume(consume_mirror_message,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

app.run(host='0.0.0.0', port=5001, debug=False)
