import weakref

from utils.vector2 import Vector2


class NineGridSensor:
    class SensorCell:
        def __init__(self, origin: Vector2, size: int):
            self.origin = origin
            self.size = size

        def point_check(self, sensor_origin: Vector2, point: Vector2) -> bool:
            diff = point - sensor_origin
            return (self.origin.x <= diff.x < (self.origin.x + self.size) and
                    self.origin.y <= diff.y < (self.origin.y + self.size))

    class SensorRuntimeData:
        def __init__(self, cells):
            self._runtime = []
            for cell in cells:
                runtime_data = {
                    'objects': [],
                    'cell': cell
                }
                self._runtime.append(runtime_data)

        @property
        def cells(self):
            return self._runtime

        def reset(self):
            for runtime_cell in self._runtime:
                del runtime_cell['objects'][:]

        def check_object(self, owner_position: Vector2, object_position: Vector2, object):
            for data in self._runtime:
                if data['cell'].point_check(owner_position, object_position):
                    data['objects'].append(object)
                    return True
            return False

    def __init__(self, levels):
        self.__cells = []
        self.__generate_level(levels)

    @property
    def cells(self):
        return self.__cells

    def create_runtime_data(self):
        return NineGridSensor.SensorRuntimeData(self.__cells)

    def __add_cell(self, origin: Vector2, size: int):
        self.__cells.append(self.SensorCell(origin, size))

    def __generate_level(self, level: int):
        grid_size = 1
        parent_size = 0
        correction = 0
        if level != 0:
            parent_size, correction = self.__generate_level(level - 1)
            grid_size = parent_size * 3
        center_cell_pos = Vector2(-parent_size, -parent_size) - Vector2(correction, correction)

        # X
        self.__add_cell(center_cell_pos + Vector2(-grid_size, -grid_size), grid_size)
        self.__add_cell(center_cell_pos + Vector2(+grid_size, -grid_size), grid_size)
        self.__add_cell(center_cell_pos + Vector2(+grid_size, +grid_size), grid_size)
        self.__add_cell(center_cell_pos + Vector2(-grid_size, +grid_size), grid_size)

        # +
        self.__add_cell(center_cell_pos + Vector2(0, -grid_size), grid_size)
        self.__add_cell(center_cell_pos + Vector2(+grid_size, 0), grid_size)
        self.__add_cell(center_cell_pos + Vector2(0, +grid_size), grid_size)
        self.__add_cell(center_cell_pos + Vector2(-grid_size, 0), grid_size)

        return grid_size, correction + parent_size
