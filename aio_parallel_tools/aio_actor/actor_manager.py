import random
_registry_class = {}


class ActorManagerRegister(type):

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        cls.Members = set()
        _registry_class[cls.__name__] = cls
        return cls


def has_actor():
    return list(_registry_class.keys())


def get_actor(class_name):
    return _registry_class.get(class_name)
