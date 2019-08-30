import time
import asyncio
import importlib
from pathlib import Path

"""
Gracefully deploys newer versions of the firebasePush script upon detecting a
flag set by the git pull script.
"""

class FileExistsFlag:
    def __init__(self, path):
        self.path = Path(path)

    def flagged(self):
        return self.path.exists()

    def unflag(self):
        self.path.unlink()

    def __bool__(self):
        return self.flagged()

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

if __name__ == '__main__':
    flag = FileExistsFlag('tmp/cronlog/laundro_git_pull_as_run')
    script = VersionManager('firebasePush.py')
    script.run(flag=flag, interval=300)
