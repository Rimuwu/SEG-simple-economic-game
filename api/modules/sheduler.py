from typing import Callable
from modules.json_database import just_db
from modules.function_way import *
import asyncio
from datetime import datetime
import json


class TaskScheduler:
    def __init__(self, db=just_db):
        self.db = db
        self.running = False
        self._init_schedule_table()

    def _init_schedule_table(self):
        tables = self.db.get_tables()
        if 'time_schedule' not in tables:
            self.db.create_table('time_schedule')

    async def start(self):
        if self.running:
            return
        self.running = True
        asyncio.create_task(self._run_scheduler())

    def stop(self):
        self.running = False

    async def _run_scheduler(self):
        while self.running:
            try:
                await self._check_and_execute_tasks()
            except Exception as e:
                print(f"Ошибка в планировщике: {e}")
            await asyncio.sleep(1)
    
    async def _check_and_execute_tasks(self):
        current_time = datetime.now()
        tasks = self.db.find('time_schedule')
        
        for task in tasks:
            task_time = datetime.fromisoformat(task['execute_at'])
            if task_time <= current_time:
                await self._execute_task(task)
    
    async def _execute_task(self, task):
        func = str_to_func(task['function_path'])
        args = json.loads(task.get('args', '[]'))
        kwargs = json.loads(task.get('kwargs', '{}'))
        repeat = task.get('repeat', False)
        add_at = datetime.fromisoformat(task['add_at'])
        execute_at = datetime.fromisoformat(task['execute_at'])

        try:
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        except Exception as e:
            print(f"Ошибка при выполнении задачи {task['function_path']}: {e}")

        if repeat:
            interval = execute_at - add_at
            next_execute_time = datetime.now() + interval
            self.db.update('time_schedule', {'id': task['id']}, {'execute_at': next_execute_time.isoformat()})

        else:
            self.db.delete('time_schedule', id=task['id'])

    def schedule_task(self, function: Callable, 
                      execute_at: datetime, 
                      args: list = None, 
                      kwargs: dict = None,
                      repeat: bool = False,
                      delete_on_shutdown: bool = False) -> int:
        if args is None: args = []
        if kwargs is None: kwargs = {}

        task_data = {
            'function_path': func_to_str(function),
            'execute_at': execute_at.isoformat(),
            'add_at': datetime.now().isoformat(),
            'args': json.dumps(args),
            'kwargs': json.dumps(kwargs),
            'repeat': repeat,
            'delete_on_shutdown': delete_on_shutdown
        }

        return self.db.insert('time_schedule', task_data)

    def cleanup_shutdown_tasks(self):
        """
        Удаляет все задачи, помеченные для удаления при завершении работы API.
        Этот метод следует вызывать при завершении работы приложения.
        """
        try:
            deleted_count = self.db.delete('time_schedule', delete_on_shutdown=True)
            print(f"Удалено {deleted_count} задач при завершении работы")
            return deleted_count
        except Exception as e:
            print(f"Ошибка при удалении задач завершения: {e}")
            return 0


scheduler = TaskScheduler()