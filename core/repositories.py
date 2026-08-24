# core/repositories.py
"""
DATA ACCESS LAYER: Repository Interfaces & Loose Coupling Adapters
Enables Dependency Injection and seamless swapping between In-Memory Mock and SQLite providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import sqlite3
import os

# 1. ABSTRACT REPOSITORY INTERFACE
class IRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def delete(self, record_id: Any) -> bool:
        pass


# 2. IN-MEMORY REPOSITORY (For Unit Testing & Rapid Mocking)
class InMemoryRepository(IRepository):
    def __init__(self, initial_data: Optional[List[Dict[str, Any]]] = None):
        self._storage: Dict[Any, Dict[str, Any]] = {}
        self._auto_id = 1
        if initial_data:
            for item in initial_data:
                rec_id = item.get("id", self._auto_id)
                self._storage[rec_id] = dict(item)
                if isinstance(rec_id, int) and rec_id >= self._auto_id:
                    self._auto_id = rec_id + 1

    def get_all(self) -> List[Dict[str, Any]]:
        return [dict(v) for v in self._storage.values()]

    def get_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        record = self._storage.get(record_id) or self._storage.get(str(record_id))
        return dict(record) if record else None

    def insert(self, data: Dict[str, Any]) -> Any:
        new_record = dict(data)
        if "id" not in new_record or new_record["id"] is None:
            new_id = self._auto_id
            self._auto_id += 1
            new_record["id"] = new_id
        else:
            new_id = new_record["id"]
        self._storage[new_id] = new_record
        return new_id

    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        key = record_id if record_id in self._storage else str(record_id)
        if key not in self._storage:
            return False
        self._storage[key].update(data)
        return True

    def delete(self, record_id: Any) -> bool:
        key = record_id if record_id in self._storage else str(record_id)
        if key in self._storage:
            del self._storage[key]
            return True
        return False


# 3. SQLITE REPOSITORY (Production Implementation)
class SQLiteRepository(IRepository):
    def __init__(self, table_name: str, db_path: str):
        self.table_name = table_name
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all(self) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        id_col = "id"
        rows = conn.execute(f"SELECT * FROM {self.table_name} ORDER BY {id_col} DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_id(self, record_id: Any) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        id_col = "id"
        row = conn.execute(f"SELECT * FROM {self.table_name} WHERE {id_col} = ?", (record_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def insert(self, data: Dict[str, Any]) -> Any:
        conn = self._get_connection()
        cursor = conn.cursor()
        columns = [k for k in data.keys() if k != 'id' or self.table_name == 'adt_beds']
        placeholders = ['?'] * len(columns)
        values = [data[k] for k in columns]
        sql = f"INSERT OR REPLACE INTO {self.table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, values)
        conn.commit()
        new_id = cursor.lastrowid or data.get('id')
        conn.close()
        return new_id

    def update(self, record_id: Any, data: Dict[str, Any]) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        columns = [k for k in data.keys() if k != 'id']
        set_clause = ', '.join([f"{k} = ?" for k in columns])
        values = [data[k] for k in columns]
        values.append(record_id)
        id_col = "id"
        sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_col} = ?"
        cursor.execute(sql, values)
        conn.commit()
        affected = cursor.rowcount > 0
        conn.close()
        return affected

    def delete(self, record_id: Any) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        id_col = "id"
        sql = f"DELETE FROM {self.table_name} WHERE {id_col} = ?"
        cursor.execute(sql, (record_id,))
        conn.commit()
        affected = cursor.rowcount > 0
        conn.close()
        return affected
