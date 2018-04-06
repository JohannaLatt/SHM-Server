from flask import Flask
import _thread
from . import messaging as Messaging
from . import modules as Modules

PORT = 5001

app = Flask(__name__)

Modules.initiate_modules()
_thread.start_new_thread(Messaging.initiate_messaging, ())

app.run(host='0.0.0.0', port=PORT, debug=False)
