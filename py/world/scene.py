from utils.vector2 import Vector2
from view.base import BaseView
from world.objects import BaseObject


class Scene(object):
    def __init__(self):
        self.objects = []
        self._view = None  # type: BaseView

    def __add__(self, object):
        if not isinstance(object, BaseObject):
            raise TypeError("Wrong type")

        object.set_scene(self)

        if object not in self.objects:
            self.objects.append(object)

        return self

    def __sub__(self, obj):
        if not isinstance(obj, BaseObject):
            raise TypeError("Wrong type")

        obj.set_scene(None)

        if obj in self.objects:
            self.objects.remove(obj)

        return self

    def clear(self):
        for obj in self.objects:
            obj.set_view(None)

        self.objects.clear()

    def setView(self, view: BaseView):
        self._view = view

    def update(self):
        for obj in self.objects:
            obj.update()

    def draw(self, view: BaseView):
        for obj in self.objects:
            obj.draw(view)

    def move_object(self, object: BaseObject, position: Vector2) -> Vector2:
        raise NotImplemented

