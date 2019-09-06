import importlib
import time
from multiprocessing import Process

class ReloadableModule:
    def __init__(self, name):
        name = name.replace('.py', '')
        self.module = importlib.import_module(name)

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

if __name__ == '__main__':
    run_with_updates('test.py', 'main', update_interval=1)
    # run_with_updates('firebasePush.py', 'main', update_interval=1)
