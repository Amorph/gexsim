
class Event:
    def __init__(self):
        self.__callbacks = []

    def __iadd__(self, func):
        if not callable(func):
            raise TypeError('Wrong type from event:' + str(type(func)))
        self.__callbacks.append(func)
        return self

    def __isub__(self, func):
        self.__callbacks.remove(func)
        return self

    def __call__(self, *args, **kwargs):
        for callback in self.__callbacks:
            callback(*args, **kwargs)