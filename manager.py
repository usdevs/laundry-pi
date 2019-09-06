import time
import asyncio
import importlib
from pathlib import Path

import inspect

!echo def foo(): print('foo!') > a.py
module = importlib.import_module('a')
module = importlib.reload(module)
method = getattr(module, 'foo')
method()
module

"""
Gracefully deploys newer versions of the firebasePush script upon detecting a
flag set by the git pull script.
"""

class Flag:
    def flag(self):
        raise NotImplementedError()
    def unflag(self):
        raise NotImplementedError()
    def flagged(self):
        raise NotImplementedError()
    def __bool__(self):
        return self.flagged()

class FileExistsFlag:
    def __init__(self, path):
        self.path = Path(path)

    def flag(self):
        try:
            self.path.touch()
        except FileExistsError:
            pass # already flagged

    def unflag(self):
        self.path.unlink()

    def flagged(self):
        return self.path.exists()

class VersionManager:
    def __init__(self, module, **kwargs):
        Process.__init__(self, **kwargs)
        self.module = importlib.import_module(module.replace('.py', ''))

    def run(self, *arg, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())

    async def shutdown(self, loop):
        """Gracefully halts execution and executes all remaining tasks in an event loop"""
        tasks = (t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task(loop))
        await asyncio.gather(*tasks)
        loop.stop()

    async def main(self, flag, interval):
        loop = asyncio.new_event_loop()
        loop.create_task(self.module.main())
        while True:
            time.sleep(interval)
            if flag.flagged():
                # Halt execution of code
                await self.shutdown(loop)

                # Restart new code
                self.module = importlib.reload(self.module)
                task = asyncio.schedule_task(self.module.main())

                # Reset flag
                flag.unflag()

class ReloadableAsyncModule:
    def __init__(self, name):
        self.module = importlib.import_module(name)
        self.loop = asyncio.get_event_loop()

    def run_until(self, name, flag, interval=None):
        loop = asyncio.new_event_loop()

    def run_until(self, name, flag, interval=None):
        """Runs a coroutine and reloads it every time the flag is set"""
        self.run_coroutine(name)
        while True:
            if interval != None:
                time.sleep(interval) # Make the process less intesive?
            if not flag.flagged():
                self.reload()
                self.run_coroutine(name)
                flag.unflag()

    def run_coroutine(self, name):
        try:
            coroutine = getattr(self.module, name)
            self.loop.run_forever(coroutine())
        except AttributeError:
            raise ValueError('coroutine', name, 'not found in module')

    def reload(self):
        self.loop.stop()
        self.module = importlib.reload(self.module)

async def block_until(flag):
    while True:
        if flag.flagged():
            return True

async def check_flag(coroutine, flag):
    tasks = [
        coroutine(),
        block_until(flag),
    ]
    tasks = [asyncio.create_task(t) for t in tasks]
    await asycio.wait(tasks, return_when=FIRST_COMPLETED)


if __name__ == '__main__':
    flag = FileExistsFlag('tmp/cronlog/laundro_git_pull_as_run')
    module = ReloadableAsyncModule('firebasePush')
    module.run_until(name='main', flag=flag)
