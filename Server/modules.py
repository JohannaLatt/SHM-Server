import configparser
import importlib

# Instantiate all modules from the config
modules = []


def initiate_modules():
    Config = configparser.ConfigParser()
    Config.read('./config/mirror_config.ini')
    module_config_names = Config.get('General', 'module_names').split(',')
    for module_config_name in module_config_names:
        module_path = Config.get(module_config_name, 'path_name')
        module_class = Config.get(module_config_name, 'class_name')
        print("Initiating %r at %r\n" % (module_class, module_path))
        #module = importlib.import_module('formmodules."+my_module)

        #module = importlib.import_module(module_path)
        #class_ = getattr(module, module_class)
        #instance = class_()
        #modules.append(instance)

        #loader = importlib.machinery.SourceFileLoader(module_class, module_path)
        #mod = types.ModuleType(loader.name)
        #loader.exec_module(mod)
        #modules.append(mod)
