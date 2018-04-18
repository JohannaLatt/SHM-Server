from flask import Flask

import threading

from Server import messaging as Messaging
from Server import module_manager as ModuleManager

PORT = 5001

app = Flask(__name__)

Messaging.init()
thread = threading.Thread(target=Messaging.start_sending)
thread.daemon = True
thread.start()

# Initiate the modules before starting to consume messages
ModuleManager.initiate_modules(Messaging)
thread = threading.Thread(target=Messaging.start_consuming)
thread.daemon = True
thread.start()

app.run(host='0.0.0.0', port=PORT, debug=False)
