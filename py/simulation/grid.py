import math
import random

from genetic.dna import DNASequence
from genetic.generator import decompile, assemble
from genetic.mutate import mutate
from nn.nodes import NeuralNetwork
from nn.visualizer import draw_network
from simulation.base import BaseSimulation, BaseExperimentController
from simulation.functions import set_scene, set_random_seed
from utils.input import Keys
from utils.sensors import NineGridSensor
from utils.vector2 import Vector2
from utils.vector3 import Vector3
from view.base import BaseView
from world.objects import Box, BaseObject
from world.scene import Scene

nine_grid_sensor3 = NineGridSensor(4)


class GridScene(Scene):
    def __init__(self, context):
        super(GridScene, self).__init__()
        self._gridSize = Vector2(100, 100)
        self._gridData = [None for _ in range(self._gridSize.x * self._gridSize.y)]
        self._drawGrid = False

    def setView(self, view: BaseView):
        super(GridScene, self).setView(view)

    def draw(self, view: BaseView):
        if self._drawGrid:
            color = Vector3(.1, .1, .1)
            lt = Vector2(0, 0) * self._gridSize
            rt = Vector2(1, 0) * self._gridSize
            rb = Vector2(1, 1) * self._gridSize
            lb = Vector2(0, 1) * self._gridSize

            view.draw_line(lt, rt, color)
            view.draw_line(rt, rb, color)
            view.draw_line(rb, lb, color)
            view.draw_line(lb, lt, color)

            for i in range(self._gridSize.x - 1):
                offset = Vector2(1.0 * (i + 1), 0)
                view.draw_line(lt + offset, lb + offset, color)

            for i in range(self._gridSize.y - 1):
                offset = Vector2(0.0, 1.0 * (i + 1))
                view.draw_line(lt + offset, rt + offset, color)

        super(GridScene, self).draw(view)

    def move_object(self, object: BaseObject, position: Vector2):
        roundPos = Vector2(math.trunc(position.x), math.trunc(position.y))
        roundPos.clamp(Vector2.ZERO, self._gridSize - Vector2.ONE)
        if object.position == roundPos:
            return None

        objAtNewPos = self.getObjectAtPosition(position)
        if objAtNewPos:
            if object.capture(objAtNewPos):
                objAtNewPos.captured(object)
                self.__sub__(objAtNewPos)
            elif objAtNewPos.capture(object):
                object.captured(objAtNewPos)
                self.__sub__(object)
            else:
                return None

        return roundPos

    def getObjectAtPosition(self, position: Vector2):
        roundPos = Vector2(math.trunc(position.x), math.trunc(position.y))
        for object in self.objects:
            if object.position == roundPos:
                return object
        return None


class Creature(Box):
    MAX_LIFE = 100
    INPUT_COUNT = 1 + len(nine_grid_sensor3.cells)
    OUTPUT_COUNT = 2

    def __init__(self, context):
        super(Creature, self).__init__()

        data = context['data']
        population = context['population_controller']
        self.consumed = 0

        self.max_life = data['life']
        self.life = self.max_life
        self._sensor_data = nine_grid_sensor3.create_runtime_data()

        self.inputs = [0 for _ in range(Creature.INPUT_COUNT)]
        dna = population.get()
        self.nn = NeuralNetwork(Creature.INPUT_COUNT, Creature.OUTPUT_COUNT, [])
        self.nn.layers.clear()
        assemble(dna, self.nn)
        self.position = data['position']

    def update(self):
        if self.life < 0:
            return

        self.life -= 1

        self._sensor_data.reset()
        position = self.position
        for obj in self.scene.objects:
            if obj is self:
                continue
            self._sensor_data.check_object(position, obj.position, obj)

        self.inputs[0] = self.life / self.max_life
        for i, v in enumerate(self._sensor_data.cells):
            if v['objects']:
                self.inputs[i + 1] = 1
            else:
                self.inputs[i + 1] = 0

        output = self.nn.update(self.inputs)
        if len(output) < 2:
            return
        delta = Vector2(output[0], output[1])
        delta.clamp(Vector2.ONE * -1.0, Vector2.ONE)
        if delta != Vector2.ZERO:
            self.position += delta

    def capture(self, target_object):
        if isinstance(target_object, Food):
            self.life += target_object.energy
            self.consumed += 1
            if self.life > self.max_life:
                self.life = self.max_life
            return True
        return False

    def draw(self, view: BaseView):
        super(Creature, self).draw(view)
        # draw_network(view, self.nn, {})
        #self._draw_sensor_range(view, self._sensor_data)

    def _draw_sensor_range(self, view: BaseView, sensor_data):
        base_position = self.position
        for cell_data in sensor_data.cells:
            cell = cell_data['cell']
            color = Vector3(1, 1, 1)
            if cell_data['objects']:
                color = Vector3(1, 0, 0)
                Creature._draw_sensor_cell_range(view, cell.origin + base_position, cell.size, color)

    @staticmethod
    def _draw_sensor_cell_range(view: BaseView, cell_origin: Vector2, size: int, color: Vector3):
        bottom_right = cell_origin + Vector2(size, size)
        view.draw_line(Vector2(cell_origin.x, cell_origin.y), Vector2(bottom_right.x, cell_origin.y), color)
        view.draw_line(Vector2(bottom_right.x, cell_origin.y), Vector2(bottom_right.x, bottom_right.y), color)
        view.draw_line(Vector2(bottom_right.x, bottom_right.y), Vector2(cell_origin.x, bottom_right.y), color)
        view.draw_line(Vector2(cell_origin.x, bottom_right.y), Vector2(cell_origin.x, cell_origin.y), color)


class Food(Box):
    def __init__(self, context):
        super(Food, self).__init__()
        self.position = context['data']['position'] if 'position' in context['data'] else Vector2(30, 70)
        self.color = Vector3(0, 1, 0)
        self.energy = 100

    def update(self):
        pass


class FoodEatExperiment(BaseExperimentController):
    def __init__(self, context):
        super(FoodEatExperiment, self).__init__(context)

    def update(self):
        super(FoodEatExperiment, self).update()
        for obj in self._scene.objects:
            if isinstance(obj, Creature):
                if obj.life <= 0:
                    dna = decompile(obj.nn)
                    result = {
                        'score': self.compute_score(),
                        'dna': dna.tostring()
                    }

                    if result['score'] == 0:
                        del result['dna']

                    self.finish_experiment(result)

    def compute_score(self):
        score = 0
        for obj in self._scene.objects:
            if isinstance(obj, Creature):
                score += obj.consumed
        return score


def random_creature_spawn(context):
    # 'position': Vector2(40, 40),
    #                'life': 100,
    #                'neural_network': [14, 8, 4]}),
    return Creature(context)


class GridSimulation(BaseSimulation):
    KEY_UP = 0
    KEY_DOWN = 1
    KEY_LEFT = 2
    KEY_RIGHT = 3

    def __init__(self, data):
        super(GridSimulation, self).__init__(data)
        # self.controlObject = Creature()
        # self.scene += self.controlObject
        # self.scene += Food()

        # self.seed = 0

        self.moveKeys = [False, False, False, False]

    def restart(self):
        pass
        # self.seed += 1
        # self.controlObject.life = self.controlObject.MAX_LIFE
        # random.seed(self.seed)
        # self.scene -= self.controlObject
        # self.controlObject = Creature()
        # self.scene += self.controlObject

    def mutate(self):
        dna = decompile(self.controlObject.nn)
        mutate(dna, 10)
        self.controlObject.nn.layers.clear()
        assemble(dna, self.controlObject.nn)

    def set_view(self, view: BaseView):
        super(GridSimulation, self).set_view(view)
        # self.scene.setView(view)
        view.on_key_down += self.on_key_down
        view.on_key_up += self.on_key_up

    def on_key_down(self, key, modifier):
        if key == Keys.K_UP:
            self.moveKeys[self.KEY_UP] = True
        elif key == Keys.K_DOWN:
            self.moveKeys[self.KEY_DOWN] = True
        elif key == Keys.K_LEFT:
            self.moveKeys[self.KEY_LEFT] = True
        elif key == Keys.K_RIGHT:
            self.moveKeys[self.KEY_RIGHT] = True
        elif key == Keys.K_m:
            self.mutate()

    def on_key_up(self, key, modifier):
        if key == Keys.K_UP:
            self.moveKeys[self.KEY_UP] = False
        elif key == Keys.K_DOWN:
            self.moveKeys[self.KEY_DOWN] = False
        elif key == Keys.K_LEFT:
            self.moveKeys[self.KEY_LEFT] = False
        elif key == Keys.K_RIGHT:
            self.moveKeys[self.KEY_RIGHT] = False

    def update(self):
        super(GridSimulation, self).update()
        if False and self.controlObject:
            delta = Vector2()
            if self.moveKeys[self.KEY_UP]:
                delta.y -= 1.0
            if self.moveKeys[self.KEY_DOWN]:
                delta.y += 1.0
            if self.moveKeys[self.KEY_LEFT]:
                delta.x -= 1.0
            if self.moveKeys[self.KEY_RIGHT]:
                delta.x += 1.0
            if delta != Vector2.ZERO:
                self.controlObject.position += delta

        #self.scene.update()
        #if self.controlObject.life < 0:
        #    self.restart()

    def draw(self, view: BaseView):
        super(GridSimulation, self).draw(view)
        #self.scene.draw(view)
        #draw_network(view, self.controlObject.nn, {})


class RandomPopulation:
    def __init__(self, context, data):
        self.data = data

    def get(self):
        nn = NeuralNetwork(Creature.INPUT_COUNT, Creature.OUTPUT_COUNT, self.data['neural_network'])
        return decompile(nn)


class MutatePopulation:
    def __init__(self, context, data):
        self.context = context
        self.data = data
        current_stage = self.context['stage_index']
        self.population = []
        stages = data.get('stages', [-1])
        for stage_index in stages:
            self.population += MutatePopulation.get_stage_results(context, current_stage + stage_index)

        self.population = sorted(self.population, reverse=True, key=lambda item: item['score'])
        self.population = self.population[:data['initial_population']]

    @staticmethod
    def get_stage_results(context, index):
        if index < 0 or index >= len(context['stages']):
            return []
        results = context['stages'][index]['results']
        return [data for data in results.values() if 'dna' in data]

    def get(self):
        index = self.context['experiment']['index'] - 1
        index %= len(self.population)
        origin = self.population[index]
        dna = DNASequence()
        dna.fromstring(origin['dna'])
        mutate(dna, self.data['mutations'])
        return dna


# Simulation->Stage->Experiment
FoodFindSimulation = {
    'class': GridSimulation,
    'root_dir': 'food',
    'stages':
    [
        # Initial random NN creation
        {
            'name': 'Initial random NeuralNetwork',
            'enabled': True,
            'controller': FoodEatExperiment,
            'population': (RandomPopulation, {'neural_network': [14, 12, 4]}),
            'iterations': 10000,
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)})
            ]
        },
        # Initial random NN creation
        {
            'name': 'Initial random NeuralNetwork',
            'controller': FoodEatExperiment,
            'iterations': 10000,
            'population': (RandomPopulation, {'neural_network': [18, 14, 6]}),
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 300}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)})
            ]
        },
        {
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1, -2],
                'initial_population': 200,
                'mutants': 50,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 300,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(26, 55)}),
                (Food, {'position': Vector2(54, 17)}),
                (Food, {'position': Vector2(35, 88)}),
                (Food, {'position': Vector2(86, 70)})
            ]

        },
        {
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 100,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 300,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(16, 25)}),
                (Food, {'position': Vector2(74, 97)}),
                (Food, {'position': Vector2(55, 28)}),
                (Food, {'position': Vector2(66, 75)})
            ]
        },
        {
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 500,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)})
            ]
        },
{
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 500,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)})
            ]
        },
{
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 500,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)}),
                (Food, {'position': Vector2(16, 25)}),
                (Food, {'position': Vector2(74, 97)}),
                (Food, {'position': Vector2(55, 28)}),
                (Food, {'position': Vector2(66, 75)})
            ]
        },
{
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 500,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)}),
                (Food, {'position': Vector2(16, 25)}),
                (Food, {'position': Vector2(74, 97)}),
                (Food, {'position': Vector2(55, 28)}),
                (Food, {'position': Vector2(66, 75)})
            ]
        },
{
            'name': 'Mutate previous population',
            'controller': FoodEatExperiment,
            'population': (MutatePopulation, {
                'stages': [-1],
                'initial_population': 500,
                'mutants': 100,
                'mutations': 1}),
            'iterations': 10000,  # initial_population * mutants and each contain 100 mutations
            # 'no_store': True,
            'environment': [
                (set_scene, GridScene),
                (set_random_seed, lambda context: context['experiment']['index']),
                (random_creature_spawn, {
                    'position': Vector2(40, 40),
                    'life': 100,
                    'neural_network': [18, 14, 6]}),
                (Food, {'position': Vector2(30, 10)}),
                (Food, {'position': Vector2(74, 17)}),
                (Food, {'position': Vector2(55, 18)}),
                (Food, {'position': Vector2(66, 70)}),
                (Food, {'position': Vector2(16, 25)}),
                (Food, {'position': Vector2(74, 97)}),
                (Food, {'position': Vector2(55, 28)}),
                (Food, {'position': Vector2(66, 75)})
            ]
        },
    ]
}

