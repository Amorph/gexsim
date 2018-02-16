import os, pickle

import math

from view.base import BaseView
from world.scene import Scene


class BaseSimulation(object):
    ROOT_PATH = "simulations"

    def __init__(self, data):
        self._stages = data['stages']
        self.stage_index = -1
        self.controller = None
        self.context = {
            'dir': os.path.join(BaseSimulation.ROOT_PATH, data['root_dir']),
            'simulation': self,
            'stages': self._stages,
            'stage_index': -1,
        }
        os.makedirs(self.context['dir'], exist_ok=True)

    def start_stage(self):
        self.context['stage_index'] = (self.context['stage_index'] + 1) % len(self.context['stages'])

        stage_data = self._stages[self.context['stage_index']]
        stage_data['results'] = {}
        if not stage_data.get('enabled', True):
            self.start_stage()
            return

        self.context.update({
            'stage_data': stage_data
        })

        controller_clazz = stage_data['controller'] if ('controller' in stage_data) else BaseExperimentController
        self.context['controller'] = controller_clazz(self.context)
        self.context['controller'].load_all_data()
        self.context['controller'].start_next()

    def update(self):
        self.context['controller'].update()

    def set_view(self, view: BaseView):
        pass

    def draw(self, view: BaseView):
        self.context['controller'].draw(view)


class BaseExperimentController(object):
    def __init__(self, context):
        self.context = context
        self._score = 0
        self.iteration = 0
        self.experiment = None
        self._scene = None  # type: Scene
        self.results = {}
        stage_index = str(self.context['stage_index'])

        population_data = self.context['stage_data']['population']
        self.context['population_controller'] = population_data[0](self.context, population_data[1])

        self.context['stage_dir'] = os.path.join(self.context['dir'], stage_index)
        os.makedirs(self.context['stage_dir'], exist_ok=True)

    def reset(self):
        self.experiment = self.context['experiment'] = {'index': self.iteration}

        self.create_scene()
        self.setup_environment()

    def create_scene(self):
        self.set_scene(Scene())

    def setup_environment(self):
        environment = self.context['stage_data']['environment']
        for env_data in environment:
            self.context['data'] = env_data[1]
            scene_object = env_data[0](self.context)
            self.context['data'] = None
            if scene_object:
                self._scene += scene_object

    def set_scene(self, scene):
        if self._scene:
            self._scene.clear()
        self._scene = scene

    def finish_experiment(self, result):
        print("finished", self.context['stage_index'], self.iteration)
        result['iteration'] = self.iteration
        self.context['stage_data']['results'][self.iteration] = result
        if not self.context['stage_data'].get('no_store', False):
            name = "{}_{}".format(result['score'], self.iteration)
            file = open(os.path.join(self.context['stage_dir'], name), 'wb')
            file.write(pickle.dumps(result))
            file.close()

        self.start_next()

    def start_next(self):
        max_iterations = self.context['stage_data']['iterations']
        while True:
            self.iteration += 1
            iteration_data = self.context['stage_data']['results'].get(self.iteration)

            if iteration_data is None:
                break

        if self.iteration > max_iterations:
            self.stage_finished()
            return
        self.reset()

    def load_all_data(self):
        results = self.context['stage_data']['results']
        files = os.listdir(self.context['stage_dir'])
        count = len(files)
        print("Loading files from:", self.context['stage_dir'])
        print_precent = 0
        for index, file in enumerate(files):
            percent = math.trunc(index / float(count) * 100.0 + 0.5)
            if percent != print_precent:
                print_precent = percent
                print("{}%".format(print_precent))
            file_path = os.path.join(self.context['stage_dir'], file)
            file = open(file_path, 'rb')
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0, os.SEEK_SET)
            raw_data = file.read(size)
            data = pickle.loads(raw_data)
            results[data['iteration']] = data
            file.close()

    def stage_finished(self):
        self.context['simulation'].start_stage()

    @property
    def score(self):
        return self._score

    def finished(self):
        pass

    def update(self):
        self._scene.update()

    def draw(self, view: BaseView):
        self._scene.draw(view)


class Stage(object):
    def __init__(self):
        pass
