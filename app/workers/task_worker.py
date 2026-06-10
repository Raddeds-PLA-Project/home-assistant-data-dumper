import asyncio
from enum import Enum
from util import log

TaskState = Enum('TaskState', [
    ("COMPLETED", 2),
    ("RUNNING", 1),
    ("NOT_STARTED", 0),
    ("FAILED", -1)
])

WorkerState = Enum('WorkerState', [
    ("RUNNING", 2),
    ("IDLE", 1),
    ("NOT_STARTED", 0),
    ("SHUT_DOWN", -1)
])


# Tasks can inherit this for polymorphic behaviour
class Task:
    def __init__(self, title: str):
        self.title = title
        self.status = TaskState.NOT_STARTED
        self.type = __name__
        
    # Since this is a generic, we will just do nothing here.
    # Override this function when developing your background task
    def run(self):
        # Some code would normally run here
        self.status = TaskState.COMPLETED

# Background task runner.
class TaskWorker:
    def __init__(self):
        # Not using asyncio since I intend to store Task objects
        self.__task_queue: list[Task] = []
        self.__current_task_index = 0
        
        # Handle application shutdown smoothly
        self.__shutdown = False
        
        # Set state
        self.state = WorkerState.NOT_STARTED
        
    async def start_worker(self):
        # Begin running tasks
        log.info("Task worker started")
        self.state = WorkerState.IDLE
        
        # Loop until the shutdown signal is sent
        while not self.__shutdown:
            
            # If there are no new tasks, hold in idle state
            while self.state == WorkerState.IDLE:
                if self.__current_task_index in range(len(self.__task_queue)):
                    self.state == WorkerState.RUNNING
                    
            # Retrieve current task
            current_task = self.__task_queue[self.__current_task_index]
            
            # Run it
            try:
                log.info(f"Starting task {current_task.type}: {current_task.title}")
                await current_task.run()
                
            # If error, output it and continue
            except Exception as e:
                log.error(f"{current_task.type} {current_task.title} had an error: {e}")
                current_task.status = TaskState.FAILED
                
            # If we get here, the task was completed
            log.info(f"Completed task {current_task.type}: {current_task.title}")
            
            # If the task never marked itself as completed, mark it as completed
            if current_task.status == TaskState.NOT_STARTED:
                current_task.status = TaskState.COMPLETED
            
            # Set the worker to idle and move to the next task
            self.__task_queue += 1
            self.state = WorkerState.IDLE
            
        # Shutdown signal is sent and last task is completed.
        log.info("Shutdown signal recieved! Ending task worker.")
        self.state = WorkerState.SHUT_DOWN
            
    # When tasks are added, they will be started as soon as possible once the worker is running.
    async def add_task(self, task: Task):
        log.info(f"Added task {task.type}: {task.title}")
        self.__task_queue.append(task)
        
    # List task info, this includes the archive of completed tasks at the top.
    def list_tasks(self):
        return [{
            "type": task.type,
            "name": task.name,
            "status": task.status
        } for task in self.__task_queue]
        
    # Shuts down the task worker if it's running. This will allow the last running task to be completed.
    def shutdown(self):
        if (self.state != WorkerState.IDLE) and (self.state != WorkerState.RUNNING):
            log.warning("Task Worker recieved shutdown signal but was never started!")
        else:
            self.state = WorkerState.SHUT_DOWN