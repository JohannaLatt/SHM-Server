import pika


# Create a local messaging connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Create an exchange for the mirror-messages
channel.exchange_declare(exchange='mirror', exchange_type='direct')

# Declare a queue to be used (random name will be used)
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

# Listen to mirror messages
mirror_message_keys = ['mirror-ready', 'mirror-tracking']

for msg_keys in mirror_message_keys:
    channel.queue_bind(exchange='mirror',
                       queue=queue_name,
                       routing_key=msg_keys)


# Consume incoming messages
def consume_mirror_message(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(consume_mirror_message,
                      queue=queue_name,
                      no_ack=True)

# Instantiate all modules from the config 
