"""Verification for the todo platform's status mapping.

Home Assistant isn't a test dependency, so we stub the slice of its API that
todo.py imports, then import the real todo module and exercise the status
mapping (completed / needs_action) in both directions.

Run: python3 tests/test_todo.py
"""

import asyncio
import datetime
import enum
import importlib.util
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG_DIR = os.path.join(REPO, "custom_components", "hakanban")


def _stub_homeassistant():
    ha = types.ModuleType("homeassistant")
    ha.__path__ = []

    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    core.callback = lambda f: f

    config_entries = types.ModuleType("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})

    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    storage = types.ModuleType("homeassistant.helpers.storage")
    storage.Store = type("Store", (), {})
    dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")
    dispatcher.async_dispatcher_send = lambda *a, **k: None
    dispatcher.async_dispatcher_connect = lambda *a, **k: (lambda: None)
    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    device_registry.DeviceInfo = lambda **kw: kw

    class _DeviceEntryType(enum.Enum):
        SERVICE = "service"

    device_registry.DeviceEntryType = _DeviceEntryType
    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = object

    util = types.ModuleType("homeassistant.util")
    util.__path__ = []
    dt = types.ModuleType("homeassistant.util.dt")
    dt.DEFAULT_TIME_ZONE = datetime.timezone.utc
    uuid_mod = types.ModuleType("homeassistant.util.uuid")
    counter = {"n": 0}

    def _rid():
        counter["n"] += 1
        return f"id{counter['n']:04d}"

    uuid_mod.random_uuid_hex = _rid

    components = types.ModuleType("homeassistant.components")
    todo_comp = types.ModuleType("homeassistant.components.todo")

    class _TodoItemStatus(enum.Enum):
        NEEDS_ACTION = "needs_action"
        COMPLETED = "completed"

    class _TodoListEntityFeature(enum.IntFlag):
        CREATE_TODO_ITEM = 1
        UPDATE_TODO_ITEM = 2
        DELETE_TODO_ITEM = 4
        MOVE_TODO_ITEM = 8
        SET_DUE_DATE_ON_ITEM = 16
        SET_DUE_DATETIME_ON_ITEM = 32
        SET_DESCRIPTION_ON_ITEM = 64

    class _TodoItem:
        def __init__(self, uid=None, summary=None, status=None, due=None, description=None):
            self.uid = uid
            self.summary = summary
            self.status = status
            self.due = due
            self.description = description

    todo_comp.TodoItem = _TodoItem
    todo_comp.TodoItemStatus = _TodoItemStatus
    todo_comp.TodoListEntity = type("TodoListEntity", (), {})
    todo_comp.TodoListEntityFeature = _TodoListEntityFeature

    for name, mod in {
        "homeassistant": ha,
        "homeassistant.core": core,
        "homeassistant.config_entries": config_entries,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.storage": storage,
        "homeassistant.helpers.dispatcher": dispatcher,
        "homeassistant.helpers.device_registry": device_registry,
        "homeassistant.helpers.entity_platform": entity_platform,
        "homeassistant.util": util,
        "homeassistant.util.dt": dt,
        "homeassistant.util.uuid": uuid_mod,
        "homeassistant.util.uuid": uuid_mod,
        "homeassistant.components": components,
        "homeassistant.components.todo": todo_comp,
    }.items():
        sys.modules[name] = mod


_stub_homeassistant()

# Create the fake package so relative imports from hakanban modules resolve.
_hkpkg = types.ModuleType("hkpkg")
_hkpkg.__path__ = [PKG_DIR]
sys.modules["hkpkg"] = _hkpkg


def _load_module(pkg, name):
    spec = importlib.util.spec_from_file_location(
        f"{pkg}.{name}", os.path.join(PKG_DIR, f"{name}.py")
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"{pkg}.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


# Load the real data and todo modules using the same stub environment
_load_module("hkpkg", "const")
data_mod = _load_module("hkpkg", "data")
todo_mod = _load_module("hkpkg", "todo")

RESULTS = []


def check(name, cond):
    RESULTS.append((name, cond))
    print(("PASS" if cond else "FAIL") + " - " + name)


def main():
    # Test _to_item status mapping
    completed_card = {"id": "c1", "title": "Done", "status": data_mod.STATUS_COMPLETED, "due": None, "description": ""}
    item = todo_mod.HakanbanTodoListEntity._to_item(completed_card)
    check("_to_item completed card -> TodoItemStatus.COMPLETED", item.status == todo_mod.TodoItemStatus.COMPLETED)

    active_card = {"id": "c2", "title": "Todo", "status": data_mod.STATUS_NEEDS_ACTION, "due": None, "description": ""}
    item = todo_mod.HakanbanTodoListEntity._to_item(active_card)
    check("_to_item active card -> TodoItemStatus.NEEDS_ACTION", item.status == todo_mod.TodoItemStatus.NEEDS_ACTION)

    # Test async_update_todo_item maps HA status back to Hakanban status
    calls = []

    class FakeManager:
        boards = {}
        def cards_in_column(self, column_id):
            return []
        def update_card(self, uid, **fields):
            calls.append((uid, fields))

    manager = FakeManager()
    entity = todo_mod.HakanbanTodoListEntity(manager, "b1", "c1")
    entity.hass = None

    completed_item = todo_mod.TodoItem(uid="c1", summary="Done", status=todo_mod.TodoItemStatus.COMPLETED, due=None)
    asyncio.run(entity.async_update_todo_item(completed_item))
    check("update_todo_item completed -> status completed", calls and calls[-1][1].get("status") == data_mod.STATUS_COMPLETED)

    active_item = todo_mod.TodoItem(uid="c2", summary="Todo", status=todo_mod.TodoItemStatus.NEEDS_ACTION, due=None)
    asyncio.run(entity.async_update_todo_item(active_item))
    check("update_todo_item needs_action -> status needs_action", calls and calls[-1][1].get("status") == data_mod.STATUS_NEEDS_ACTION)

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed")
    sys.exit(0 if passed == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
