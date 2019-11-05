"""Define task object to send to worker."""
import asyncio
from typing import Dict, List, Any, Callable, NamedTuple


class Task(NamedTuple):
    """Task object to send to worker."""

    fut: asyncio.Future
    task_func: Callable[[Any], Any]
    args: List[Any]
    kwargs: Dict[str, Any]
