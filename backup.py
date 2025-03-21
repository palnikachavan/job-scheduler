import sched
import time
import threading

scheduler = sched.scheduler(time.time, time.sleep)

jobs = {}

def func(msg: str, duration: int):
    print(f"[{time.strftime('%H:%M:%S')}] Starting: {msg}")
    time.sleep(duration)
    print(f"[{time.strftime('%H:%M:%S')}] Finished: {msg}")

def task_wrapper(callable_func, *args):
    thread = threading.Thread(target=callable_func, args=args)
    thread.start()

def add_job(name: str, prio: int, callable_func, *args):
    """Adds a job to the scheduler and stores it in the dictionary."""
    event = scheduler.enter(3, prio, task_wrapper, argument=(callable_func, *args))  
    jobs[name] = event
    print(f'Job "{name}" added with priority {prio}')
    return event

def delete_job(name: str):
    """Deletes a specific job from the scheduler if it exists."""
    if name in jobs:
        try:
            scheduler.cancel(jobs[name])  
            print(f'Job "{name}" has been removed.')
            del jobs[name] 
        except ValueError:
            print(f'Job "{name}" has already executed or does not exist.')
    else:
        print(f'Job "{name}" not found.')

def initiate_execution():
    threading.Thread(target=run_scheduler, daemon=True).start()

def run_scheduler():
    while True:
        scheduler.run(blocking=False)
        time.sleep(1)

# adding tasks
add_job("Task1", 1, func, "Task1 running", 5)
add_job("Task2", 4, func, "Task2 running", 7)
add_job("Task3", 2, func, "Task3 running", 4)
add_job("Task4", 7, func, "Task4 running", 6)
add_job("Task5", 2, func, "Task5 running", 3)

print("\nScheduled Tasks:")
for name, event in jobs.items():
    print(f"Job Name: {name}, Time: {time.strftime('%H:%M:%S', time.localtime(event.time))}, Priority: {event.priority}")

# delete a specific job
delete_input = input("\nEnter job name to delete (or press Enter to skip): ")
if delete_input:
    delete_job(delete_input)

# handle execution initiation of scheduled ones
if input("\nStart execution? (y/n): ").lower() == 'y':
    initiate_execution()
else:
    print("Execution cancelled.")

while True:
    time.sleep(5)
