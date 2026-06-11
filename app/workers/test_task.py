from .task_worker import Task, TaskState
from util import log
import random
from time import sleep

class TestTask(Task):
    def __init__(self, title: str):
        self.time = random.randint(5, 25)
        log.info(f"Test task {title} of time {self.time} created")
        super().__init__(title, description=f"Will burn time for {self.time}")
        
    def run(self):
        self.status = TaskState.RUNNING
        log.info(f"Test task {self.title} running for {self.time} seconds")
        time_remaining = self.time
        while time_remaining > 0:
            self._update_description(f"{time_remaining} out of {self.time} seconds to burn")
            sleep(1)
            time_remaining -= 1
        self._update_description(f"Successfully burnt {self.time} seconds")
        self.status = TaskState.COMPLETED