"""
Лёгкая JSON база данных для игры
Поддерживает CRUD операции, индексы и кэширование
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import threading
from copy import deepcopy


class JSONDatabase:
    """Простая JSON база данных с поддержкой индексов и кэширования"""
    
    def __init__(self, db_path: str = "data/sessions.json", auto_save: bool = True):
        self.db_path = Path(db_path)
        self.auto_save = auto_save
        self._data: Dict[str, List[Dict]] = {}
        self._indexes: Dict[str, Dict[str, List[int]]] = {}
        self._lock = threading.RLock()
        
        # Создаём директорию если её нет
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем данные
        self.load()
    
    def load(self):
        """Загружает данные из файла"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                self._rebuild_indexes()
            except (json.JSONDecodeError, FileNotFoundError):
                self._data = {}
                self._indexes = {}
    
    def save(self):
        """Сохраняет данные в файл"""
        with self._lock:
            # Создаём backup
            if self.db_path.exists():
                backup_path = self.db_path.with_suffix('.backup.json')
                self.db_path.rename(backup_path)
            
            try:
                with open(self.db_path, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
                
                # Удаляем backup если сохранение прошло успешно
                backup_path = self.db_path.with_suffix('.backup.json')
                if backup_path.exists():
                    backup_path.unlink()
                    
            except Exception as e:
                # Восстанавливаем из backup
                backup_path = self.db_path.with_suffix('.backup.json')
                if backup_path.exists():
                    backup_path.rename(self.db_path)
                raise e
    
    def _rebuild_indexes(self):
        """Перестраивает индексы"""
        self._indexes = {}
        for table_name, records in self._data.items():
            self._indexes[table_name] = {}
            for i, record in enumerate(records):
                for key, value in record.items():
                    if key not in self._indexes[table_name]:
                        self._indexes[table_name][key] = {}
                    
                    str_value = str(value)
                    if str_value not in self._indexes[table_name][key]:
                        self._indexes[table_name][key][str_value] = []
                    
                    self._indexes[table_name][key][str_value].append(i)
    
    def create_table(self, table_name: str):
        """Создаёт новую таблицу"""
        with self._lock:
            if table_name not in self._data:
                self._data[table_name] = []
                self._indexes[table_name] = {}
                if self.auto_save:
                    self.save()
    
    def insert(self, table_name: str, record: Dict[str, Any]) -> int:
        """Вставляет запись в таблицу"""
        with self._lock:
            if table_name not in self._data:
                self.create_table(table_name)
            
            # Добавляем автоматические поля
            record = deepcopy(record)
            if 'id' not in record:
                record['id'] = len(self._data[table_name]) + 1
            record['created_at'] = datetime.now().isoformat()
            record['updated_at'] = datetime.now().isoformat()
            
            # Добавляем запись
            index = len(self._data[table_name])
            self._data[table_name].append(record)
            
            # Обновляем индексы
            if table_name not in self._indexes:
                self._indexes[table_name] = {}
            
            for key, value in record.items():
                if key not in self._indexes[table_name]:
                    self._indexes[table_name][key] = {}
                
                str_value = str(value)
                if str_value not in self._indexes[table_name][key]:
                    self._indexes[table_name][key][str_value] = []
                
                self._indexes[table_name][key][str_value].append(index)
            
            if self.auto_save:
                self.save()
                
            return record['id']
    
    def find(self, table_name: str, **conditions) -> List[Dict[str, Any]]:
        """Находит записи по условиям"""
        if table_name not in self._data:
            return []
        
        if not conditions:
            return deepcopy(self._data[table_name])
        
        # Используем индексы для быстрого поиска
        result_indexes = None
        
        for key, value in conditions.items():
            if (table_name in self._indexes and 
                key in self._indexes[table_name] and 
                str(value) in self._indexes[table_name][key]):
                
                indexes = set(self._indexes[table_name][key][str(value)])
                if result_indexes is None:
                    result_indexes = indexes
                else:
                    result_indexes = result_indexes.intersection(indexes)
            else:
                result_indexes = set()
                break
        
        if result_indexes is not None:
            return [deepcopy(self._data[table_name][i]) for i in result_indexes]
        
        # Fallback к линейному поиску
        results = []
        for record in self._data[table_name]:
            match = True
            for key, value in conditions.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                results.append(deepcopy(record))
        
        return results
    
    def find_one(self, table_name: str, **conditions) -> Optional[Dict[str, Any]]:
        """Находит одну запись"""
        results = self.find(table_name, **conditions)
        return results[0] if results else None
    
    def update(self, table_name: str, conditions: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Обновляет записи"""
        if table_name not in self._data:
            return 0
        
        with self._lock:
            updated_count = 0
            
            for i, record in enumerate(self._data[table_name]):
                match = True
                for key, value in conditions.items():
                    if key not in record or record[key] != value:
                        match = False
                        break
                
                if match:
                    # Удаляем старые индексы
                    for key, value in record.items():
                        if (table_name in self._indexes and 
                            key in self._indexes[table_name] and 
                            str(value) in self._indexes[table_name][key]):
                            self._indexes[table_name][key][str(value)].remove(i)
                    
                    # Обновляем запись
                    record.update(updates)
                    record['updated_at'] = datetime.now().isoformat()
                    
                    # Добавляем новые индексы
                    for key, value in record.items():
                        if key not in self._indexes[table_name]:
                            self._indexes[table_name][key] = {}
                        
                        str_value = str(value)
                        if str_value not in self._indexes[table_name][key]:
                            self._indexes[table_name][key][str_value] = []
                        
                        if i not in self._indexes[table_name][key][str_value]:
                            self._indexes[table_name][key][str_value].append(i)
                    
                    updated_count += 1
            
            if updated_count > 0 and self.auto_save:
                self.save()
            
            return updated_count
    
    def delete(self, table_name: str, **conditions) -> int:
        """Удаляет записи"""
        if table_name not in self._data:
            return 0
        
        with self._lock:
            records_to_delete = []
            
            for i, record in enumerate(self._data[table_name]):
                match = True
                for key, value in conditions.items():
                    if key not in record or record[key] != value:
                        match = False
                        break
                if match:
                    records_to_delete.append(i)
            
            # Удаляем записи (в обратном порядке чтобы не сбить индексы)
            for i in reversed(records_to_delete):
                del self._data[table_name][i]
            
            # Перестраиваем индексы
            self._rebuild_indexes()
            
            if records_to_delete and self.auto_save:
                self.save()
            
            return len(records_to_delete)
    
    def count(self, table_name: str, **conditions) -> int:
        """Считает количество записей"""
        return len(self.find(table_name, **conditions))
    
    def get_tables(self) -> List[str]:
        """Возвращает список таблиц"""
        return list(self._data.keys())
    
    def drop_table(self, table_name: str):
        """Удаляет таблицу"""
        with self._lock:
            if table_name in self._data:
                del self._data[table_name]
            if table_name in self._indexes:
                del self._indexes[table_name]
            
            if self.auto_save:
                self.save()

db_sessions = JSONDatabase()