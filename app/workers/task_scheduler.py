from .task_worker import Task, TaskWorker
import datetime
from util import log
import asyncio


# A Task Schedule entry
class ScheduleEntry:
    def __init__(self, queue_at: datetime.datetime, task: Task, daily = False):
        self.queue_time = queue_at # The time to run this task.
        self.task = task # The task to run
        self.daily = daily # Run daily? (Will automatically reschedule for the same time next day, in perpetuity)

    # Prints the schedule
    def info(self):
        return {
            "task": self.task.info(),
            "scheduled_for": self.queue_at,
            "daily": self.daily
        }
        

# The Task Scheduler.
class TaskScheduler:
    def __init__(self, task_worker: TaskWorker):
        self.__entry_list: list[ScheduleEntry] = []
        self.__task_worker = task_worker

        # Smoothly handle application shutdown
        self.__shutdown = False

    # Add an entry to the schedule
    def add_schedule_entry(self, entry: ScheduleEntry):
        # Add to list
        self.__entry_list.append(entry)
        # Log scheduled entry
        log.info(f"Scheduled task {entry.task.type} {entry.task.title} will run at {entry.queue_time.isoformat()}") # TODO: Include the date and time it was scheduled

    # Adding the scheduled task to the task worker instead of running it here means that a long blocking task will not affect the schedule
    def __fire_schedule_entry(self, entry: ScheduleEntry):
        # Log fired schedule entry
        log.info(f"Scheduled task {entry.task.type} {entry.task.title} fired! Added to Task Worker.")
        # Add to worker
        self.__task_worker.add_task(entry.task)
        # If entry is daily, reschedule for the next day
        self.add_schedule_entry(
            ScheduleEntry(
                queue_at = entry.queue_time + datetime.timedelta(days=1),
                task = entry.task,
                daily = True
            )
        )

    # List the entries currently in the schedule        
    def list_schedule_entries(self):
        return [entry.info() for entry in self.__entry_list]
    
    # Run the scheduler asynchronously
    async def start_scheduler(self):
        while not self.__shutdown:
            # For all tasks, if the task time is later than the current time, run it and pop it from the list
            current_time = datetime.datetime.now()
            for idx, entry in enumerate(self.__entry_list):
                if current_time < entry.queue_time:
                    # Run the task
                    self.__fire_schedule_entry(entry)
                    # Pop it from the list
                    self.__entry_list.pop(idx)
                    pass
            await asyncio.sleep(15) # Sleep for 15 seconds, we don't need terribly large precision
        log.info("Shutdown schedule recieved! Terminating scheduler")
        
    # Shut down the scheduler cleanly
    def shutdown(self):
        self.__shutdown = True