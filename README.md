# Smart-Health-Mirror: Server-Module

The server is the core of the [Smart Health Mirror framework](https://github.com/JohannaLatt/Master-Thesis-Smart-Health-Mirror). It receives incoming data from the [kinect](https://github.com/JohannaLatt/SHM-Kinect) and preprocesses that data into the expected format which consists of a bone- and a joint-mapping.

```
Joints:
{
  'SpineBase': [331.2435, -419.485077, 2150.36621], 
  'SpineMid': [313.7696, -185.470459, 1992.33936], 
  'Neck': [294.341644, 44.1935768, 1821.40552], 
  'Head': [301.3063, 171.161179, 1819.05847], ...
 }
 
Bones:
{
  'ClavicleRight': ['SpineShoulder', 'ShoulderRight'],
  'ShinLeft': ['KneeLeft', 'AnkleLeft'], ...
}
``` 

After the preprocessing, the main modules of the server are triggered and they all work on the preprocessed data, i.e. expect the format specified above. Each module does their own independent processing of that data and can then either trigger further internal actions or communicate with the [mirror](https://github.com/JohannaLatt/SHM-Mirror).

The modules the server consists of can be specified in a config-file. At startup, the server starts one thread per module and each module receives its own message-queue. Incoming external and internal messages are distributed to all modules via their own message queues so that they can handle the incoming data in their own time without potentially impairing other modules that might be more performant.

Each module has multiple triggers that it can use to do its respective tasks. Currently these triggers are:
* External Triggers (normally used by preprocessing modules)
  * User detected by tracking device
  * New skeletal tracking data available
  * Tracking device lost tracking 
  * Mirror connected
* Internal Triggers (normally used by main modules and triggerd by preprocessing or main modules)
  * New preprocessed skeletal data is available
  * User changed exercise status (not exercising vs doing specific exercise)
  * User switched exercise stage (e.g. switching from going down to going up during a squat)
  * User finished a repetition of an exercise
  
 Example modules already inluced in the framework are:
 * Kinect preprocessing-module
   * Trigger: New skeletal tracking data available
   * Action: Turns incoming data into the server-wide format outlined above. In this case the conversion is simple since the incoming data is already in the correct format.
 * Welcome-module: 
   * Trigger: Mirror connected
   * Action: Displays a simple welcome action on the mirror whenever a mirror connects to the device
 * Logging-module:
   * Trigger: New preprocessed skeletal data is available
   * Action: Logs the new data into a log-file. The resulting log-file can directly be fed into the streaming simulator as mentioned [here](#Kinect). 
 * Render Skeleton-module
   * Trigger: New preprocessed skeletal data is available
   * Action: Sends the preprocessed data to the mirror so that the mirror can render the user's skeleton
 * Recognize Squat-module
   * Trigger: New preprocessed skeletal data is available
   * Action: Analyses the user's skeleton to tell whether the user is currently doing a squat, whether he is going down or up and whether he finished a repetition. This module triggers exercise-related internal triggers.
 * Evaluate Squat-module
   * Trigger: New preprocessed skeletal data is available & User finished a repetition of an exercise
   * Action: Evaluates a squat and gives feedback to the user by sending messages to the mirror. It evaluates whether the user keeps his head straight, whether the user keeps his shoulders straight and whether the user goes low enough during the squat. This module is highly customizable through the config-file.
 * Render Spine Graph-module
   * Trigger: New preprocessed skeletal data is available
   * Action: Takes the data of a specific, configurable joint (currently the SpineBase-joint) and sends that data to the mirror to visualize the movement in x, y and z during a squat.
   
All user-related information (joints and bones as well as exercise status) is also available in a User-object that is passed on through all modules. Some modules alter that object (in a threadsafe way) and other modules read from it. This avoids sending data between modules. Instead, this object capsulates all the data needed by all modules. 

## Installation

The server is a simply Python flask server that we need to start:

1. Make sure to have the necessary requirements installed: `pip install -r [link to requirements.txt in Server folder]` (if you use virtual environments, make sure to activate it)
2. Go to /Server/Server in this repository: `cd Server/Server`
3. Set the `FLASK_APP`-environment variable to \_\_index\_\_.py
  * Mac/Linux: `export FLASK_APP= __index__.py`
  * Windows: `set FLASK_APP= __index__.py`
4. Update the RabbitMQ-messaging-server-ip in the [config-file](https://github.com/JohannaLatt/SHM-Server/blob/master/Server/config/mirror_config.ini) if needed
5. Run the server:
```
flask run
```
