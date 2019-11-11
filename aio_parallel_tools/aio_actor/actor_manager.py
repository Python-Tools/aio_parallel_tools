"""Functions for managing Actors."""
import random
from typing import List, Optional
from aio_parallel_tools.aio_actor.actor_abc import ActorABC
_registry_class = {}


class ActorManagerRegister(type):
    """Meta class for regist subclass for management."""

    def __new__(meta, name, bases, class_dict):
        """Set Members to all subclass and regist subclass."""
        cls = type.__new__(meta, name, bases, class_dict)
        cls.Members = set()
        if cls.__name__ != "AioActor":
            _registry_class[cls.__name__] = cls
        return cls


def has_actor() -> List[str]:
    """Get all actor name.

    Returns:
        List[str]: all actor name.

    """
    return list(_registry_class.keys())


def get_actor(actor_name: str) -> Optional[ActorABC]:
    """Get actor class by name.

    Args:
        actor_name (str): actor class's name

    Returns:
        Optional[ActorABC]: actor class

    """
    return _registry_class.get(actor_name)
