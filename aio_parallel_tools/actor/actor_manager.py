_registry = {}


class ActorManagerRegister(type):
    @classmethod
    def __prepare__(meta, name, bases):
        if _registry.get(name) is None:
            _registry[name] = set()
        return dict()


def actor_size(class_name: str):
    actor_type = _registry.get(class_name)
    return len(actor_type)
