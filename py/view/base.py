from utils.event import Event
from utils.vector2 import Vector2
from utils.vector3 import Vector3


class BaseView(object):
    def __init__(self):
        self.on_key_down = Event()
        self.on_key_up = Event()

    def update(self) -> bool:
        pass

    def sleep(self, milliseconds: float):
        pass

    def start_frame(self):
        pass

    def finish_frame(self):
        pass

    def draw_line(self, start: Vector2, end: Vector2, color: Vector3):
        raise NotImplemented

    def draw_quad(self, leftTop: Vector2, rigthBottom: Vector2, color: Vector3):
        pass
