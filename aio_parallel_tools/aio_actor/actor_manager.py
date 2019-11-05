import random
_registry_class = {}


class ActorManagerRegister(type):

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        cls.Members = set()
        _registry_class[cls.__name__] = cls
        return cls


def actor_size(class_name: str):
    actor_type = _registry_class.get(class_name).Len()
    return len(actor_type)


def get_one_actor(class_name):
    pass
