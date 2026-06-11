from .task_worker import Task, TaskWorker
import datetime
import schedule

# A Task Schedule entry:
# Note: The queue_at does not guarantee the task will run at that time. The Task will be added to the Task Worker at this time.
class ScheduleEntry:
    def __init__(self, queue_at: datetime.datetime, task: Task, daily = False):
        self.queue_at = queue_at # The time to run this task.
        self.task = task # The task to run
        self.daily = daily # Run daily? (Will automatically reschedule for the same time next day, in perpetuity)

    def info(self):
        return {
            "task": self.task.info(),
            "scheduled_for": self.queue_at,
            "daily": self.daily
        }

class TaskScheduler:
    def __init__(self, task_worker: TaskWorker):
        self.__task_list: list[ScheduleEntry] = []
        self.__task_worker = task_worker

        # Smoothly handle application shutdown
        self.__shutdown = False

    def add_schedule_entry(self, entry: ScheduleEntry):
        # Add to list
        # Schedule in library
        self.__task_list.append(entry)

    def __run_schedule_entry(self, entry: ScheduleEntry, task_list_index: int):
        # Add to worker
        # Pop entry from list
        # If entry is daily, reschedule for the next day
        pass
        
    def list_schedule(self):
        return 
    
    async def start_scheduler(self):
