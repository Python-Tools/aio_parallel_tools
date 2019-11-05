class ManageMixin:

    def __init__(self):
        self.__class__.Members.add(self)
        self.Members=None

    @classmethod
    def Send(clz, msg):
        pass

    @classmethod
    async def Scale(clz, number):
        pass

    @classmethod
    async def Throw(clz, exception):
        pass

    @classmethod
    def RunningLen(clz):
        pass

    @classmethod
    def AvailableLen(clz):
        pass

    @classmethod
    def Len(clz):
        pass
