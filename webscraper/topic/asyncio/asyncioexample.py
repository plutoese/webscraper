# coding = UTF-8

import collections
import time
from math import sqrt


class Task:

    next_id = 0

    def __init__(self, routine):
        self.id = Task.next_id
        Task.next_id += 1
        self.routine = routine


class Scheduler:

    def __init__(self):
        self.runnable_tasks = collections.deque()
        self.completed_task_result = {}
        self.failed_task_errors = {}

    def add(self, routine):
        task = Task(routine)
        self.runnable_tasks.append(task)
        return task.id

    def run_to_completion(self):
        while len(self.runnable_tasks) != 0:
            task = self.runnable_tasks.popleft()
            print('Running task {} ...'.format(task.id), end='')
            try:
                yielded = next(task.routine)
            except StopIteration as stopped:
                print('completed with result: {!r}'.format(stopped.value))
                self.completed_task_result[task.id] = stopped.value
            except Exception as e:
                print('failed with exception: {}'.format(e))
                self.failed_task_errors[task.id] = e
            else:
                assert yielded is None
                print('Now yielded')
                self.runnable_tasks.append(task)


def lucas():
    yield 2
    a = 2
    b = 1
    while True:
        yield b
        a, b = b, a + b


def async_search(iterable, predicate):
    for item in iterable:
        if predicate(item):
            return item
        yield
    raise ValueError('Not found')


def is_prime(x):
    if x < 2:
        return False
    for i in range(2, int(sqrt(x)) + 1):
        if x % i == 0:
            return False
    return True


def async_print_matches(iterable, predicate):
    for item in iterable:
        if predicate(item):
            print('Found :', item, end=', ')
        yield


def async_repetitive_message(message, interval_seconds):
    while True:
        print(message)
        start = time.time()
        expiry = start + interval_seconds
        while True:
            yield
            now = time.time()
            if now >= expiry:
                break



if __name__ == '__main__':
    scheduler = Scheduler()
    #scheduler.add(async_search(lucas(), lambda x: len(str(x)) >= 6))
    scheduler.add(async_repetitive_message('Unattended baggage will be destroyed', 2.5))
    scheduler.add(async_print_matches(lucas(), is_prime))
    scheduler.run_to_completion()

