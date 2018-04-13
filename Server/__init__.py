from flask import Flask
import _thread
from Server import messaging as Messaging
from Server import module_manager as ModuleManager

PORT = 5001

app = Flask(__name__)

Messaging.init()
Messaging.initiate_messaging_to_mirror()
Messaging.initiate_message_consuming()
_thread.start_new_thread(Messaging.start_sending, ())

# Initiate the modules before starting to consume messages
ModuleManager.initiate_modules(Messaging)

_thread.start_new_thread(Messaging.start_consuming, ())


app.run(host='0.0.0.0', port=PORT, debug=False)
