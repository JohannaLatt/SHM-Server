# Smart-Health-Mirror: Server-Module

The server is the core of the [Smart Health Mirror framework](https://github.com/JohannaLatt/Master-Thesis-Smart-Health-Mirror). It receives incoming data from the [Kinect](https://github.com/JohannaLatt/SHM-Kinect) and preprocesses that data into the expected format which consists of a bone- and a joint-mapping.

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

After the preprocessing, the main modules of the server are triggered and they all work on the preprocessed data, i.e. expect the format specified above. Each module does their own independent processing of that data and can then either trigger further internal actions or communicate with the [Mirror](https://github.com/JohannaLatt/SHM-Mirror).

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

## Add Custom Modules

To write your own module, create a new folder inside the modules-folder (either sort it into `preprocessing` or `main` to keep the structure clean) and adhere to the naming conventions: `module-[your custom module name]`. Inside that folder, create an empty `__init__.py`-file. These empty files are a python convention to  tell python that this folder contains a package so that it can be easily referenced. If needed, you can also use this file to import important dependencies or libraries needed for your module.

### Preprocessing- and Main-Modules

Main-Modules run on preprocessed data, i.e. they are not concerned with the format of the incoming tracking data but will just assume the following format:
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

Preprocessing-modules are mainly intended to be written if a new tracking system is added to the framework. Preprocessing modules receive the raw tracking data and are responsible for transforming it into the data format expected by the main-modules above. 

### Creation of your Custom Module

After creating the folder, create your actual module-file, that following the framework's naming conventions should be called `[your custom module name]-module.py`. Inside this file, declare your module as a class and make sure to **inherit from either the `AbstractMainModule` or the `AbstractPreprocessingModule`!**, depending on your use case.

A newly added, empty main-module could look like this:

```python
from Server.modules.abstract_main_module import AbstractMainModule

class NewModule(AbstractMainModule):

    def __init__(self, Messaging, queue, User):
        super().__init__(Messaging, queue, User)
        # do something

    def mirror_started(self):
        super().mirror_started()
        # do something

    def user_state_updated(self, user):
        super().user_state_updated(user)
        # do something

    def user_skeleton_updated(self, user):
        super().user_skeleton_updated(user)
        # do something
        
    def user_exercise_updated(self, user):
        super().user_exercise_updated(user)
        # do something

    def user_exercise_stage_updated(self, user):
        super().user_exercise_stage_updated(user)
        # do something

    def user_finished_repetition(self, user):
        super().user_finished_repetition(user)
        # do something
 ```

If some of the methods are not needed, they can also just be left out. 
The framework will ensure that the respective methods are called when an update to the respective data happens. 

To include the newly created module into the framework, it lastly also has to be added to the [config-file](https://github.com/JohannaLatt/SHM-Server/blob/master/Server/config/mirror_config.ini). The module-name (i.e. the class-name, in the example `CustomName`) has to be added to the list of module-names in the \[General\]-section of the config-file. Then, a new section for the new module has to be added to the end of the config-file, specifying where the framework can find the new package. Following the example, the new section would look like this:

```
[CustomModule]
path_name = main.module_custom.custom_module
class_name = CustomModule
```

In theory, the naming conventions do not have to be followed and the files can be created anywhere as long as they are correctly referenced inside the config-file and implement the necessary interfaces.

Once you start the server, the server will automatically find your newly created package based on the config-file and run your module in its own thread.
