import importlib
from multiprocessing import Process
from pathlib import Path
import time

class ReloadableModule:
    def __init__(self, name):
        name = name.replace('.py', '')
        self.module = importlib.import_module(name, package='laundry-pi')

    def reload(self):
        """Hope the target module doesn't have a reload attribute"""
        self.module = importlib.reload(self.module)

    def __getattr__(self, attr):
        try:
            return getattr(self.module, attr)
        except AttributeError:
            raise ValueError('attribute', attr, 'not found in module')

def run_with_updates(module, function, update_interval=60):
    """runs a function from a module and reloads it whenever it completes"""
    module = ReloadableModule(module)
    p = Process(target=getattr(module, function))
    p.start()

    while True:
        time.sleep(update_interval)
        if not p.is_alive():
            module.reload()
            p = Process(target=getattr(module, function))
            p.start()

def main():
    import sys

    try:
        module_name = sys.argv[1]
        method_name = sys.argv[2]
    except:
        print('Invalid arguments! use python3 runner.py [module path] [function name]')
        return

    run_with_updates(module_name, method_name, update_interval=5)

if __name__ == '__main__':
    main()
