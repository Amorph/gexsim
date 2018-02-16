import random
from threading import Thread

import time

from simulation.base import BaseSimulation
from simulation.grid import FoodFindSimulation
from view.pygame.init import PyGameView

view = PyGameView({
    'name': 'gexsim',
    'size': (600, 600)
})

def create_simulation(data):
    simulation_class = BaseSimulation
    if 'class' in data:
        simulation_class = data['class']
    return simulation_class(data)

random.seed(200)

simulation: BaseSimulation = create_simulation(FoodFindSimulation)
simulation.set_view(view)
simulation.start_stage()

while view.update():
    # time.sleep(0.1)
    #view.start_frame()
    simulation.update()
    #simulation.draw(view)
    #view.finish_frame()

view.destroy()
