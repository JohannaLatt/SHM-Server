from flask import Flask

import threading

from Server.messaging import Messaging
from Server.module_manager import ModuleManager

PORT = 5001
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# Initiate the messaging
messaging = Messaging()

# Initiate the modules before starting to consume messages
module_manager = ModuleManager(messaging)

# Start sending and consuming
thread = threading.Thread(target=messaging.start_sending)
thread.daemon = True
thread.start()

thread = threading.Thread(target=messaging.start_consuming)
thread.daemon = True
thread.start()

app.run(host='0.0.0.0', port=PORT, debug=False)
