import asyncio
import os
import sys
import types
import pytest

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Minimal fake supabase chainable query builder compatible with our Database usage
class FakeQuery:
    def __init__(self, table_name, store):
        self.table_name = table_name
        self.store = store
        self._select = None
        self._filters = []
        self._update = None
        self._insert = None
        self._order = []
        self._on_conflict = None

    # Builders
    def select(self, fields="*"):
        self._select = fields
        return self

    def eq(self, key, value):
        self._filters.append((key, value))
        return self

    def update(self, payload):
        self._update = payload
        return self

    def insert(self, payload):
        self._insert = payload
        return self

    def order(self, key, desc=False):
        self._order.append((key, desc))
        return self

    def on_conflict(self, key):
        self._on_conflict = key
        return self

    # Executes synchronously to match Database's run_in_executor usage
    def execute(self):
        table = self.store.setdefault(self.table_name, [])

        def match(row):
            for k, v in self._filters:
                if row.get(k) != v:
                    return False
            return True

        # Handle select
        if self._select is not None and self._update is None and self._insert is None:
            rows = [r for r in table if match(r)]
            return types.SimpleNamespace(data=rows)

        # Handle update
        if self._update is not None:
            updated = []
            for r in table:
                if match(r):
                    r.update(self._update)
                    updated.append(r)
            return types.SimpleNamespace(data=updated)

        # Handle insert
        if self._insert is not None:
            payload = self._insert
            if isinstance(payload, dict):
                new_row = payload.copy()
                if "id" not in new_row:
                    new_row["id"] = len(table) + 1
                # Support on_conflict(key)
                if self._on_conflict:
                    conflict_key = self._on_conflict
                    for r in table:
                        if r.get(conflict_key) == new_row.get(conflict_key):
                            return types.SimpleNamespace(data=[r])
                table.append(new_row)
                return types.SimpleNamespace(data=[new_row])
            raise ValueError("Only single-row insert supported in FakeQuery")

        return types.SimpleNamespace(data=[])


class FakeSupabaseClient:
    def __init__(self, store):
        self.store = store

    def table(self, name):
        return FakeQuery(name, self.store)


@pytest.fixture(autouse=True)
def supabase_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://test.local")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-key")


@pytest.fixture()
def fake_supabase(monkeypatch):
    store = {}

    def fake_create_client(url, key):
        return FakeSupabaseClient(store)

    # Patch the symbol imported inside backend.database
    monkeypatch.setattr("backend.database.create_client", fake_create_client)
    return store
