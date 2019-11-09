import uuid

class IdentifyMixin:

    def __init__(self):
        self._id = str(uuid.uuid4())

    @property
    def aid(self):
        return self._id