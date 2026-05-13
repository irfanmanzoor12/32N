import json
from datetime import date, datetime
from tasks_mcp.models import Task


def _serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Not serializable: {type(obj)}")


def task_response(task: Task) -> str:
    return json.dumps({"task": json.loads(task.model_dump_json())})


def error_response(msg: str) -> str:
    return msg
