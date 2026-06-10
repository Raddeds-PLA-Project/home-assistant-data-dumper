from .task_worker import Task, TaskState
from util import log
import random
from time import sleep

class TestTask(Task):
    def __init__(self, title: str):
        self.time = random.randint(5, 25)
        super().__init__(title)
        
    def run(self):
        self.status = TaskState.RUNNING
        log.info(f"Test task {self.title} running for {self.time} seconds")
        sleep(self.time)
        self.status = TaskState.COMPLETED