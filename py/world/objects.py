from utils.vector2 import Vector2
from utils.vector3 import Vector3
from view.base import BaseView


class BaseObject(object):
    def __init__(self):
        self.__position = Vector2()
        self.color = Vector3(1, 0, 0)
        self.scene = None

    def set_scene(self, scene):
        self.scene = scene

    def update(self):
        pass

    def draw(self, view: BaseView):
        pass

    def update(self):
        pass

    def capture(self, target_object):
        return False

    def captured(self, consumer):
        pass

    def set_view(self, view: BaseView):
        pass

    @property
    def position(self):
        return Vector2(self.__position.x, self.__position.y)

    @position.setter
    def position(self, pos):
        pos = self.scene.move_object(self, pos) if self.scene else pos
        if pos:
            self.__position = pos


class Box(BaseObject):
    def __init__(self):
        super(Box, self).__init__()
        self.size = Vector2(1, 1)

    def draw(self, view: BaseView):
        view.draw_quad(self.position, self.size, self.color)


class Creature(object):
    def __init__(self):
        self.position = Vector3()
        self.lookDir = Vector3(0.0, 1.0, 0.0)
