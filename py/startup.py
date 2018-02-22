import random
from threading import Thread

import time

import gexnetpy

net = gexnetpy.network_create(2, 4)
net.nodes[0].bias = 0.3
net.nodes[1].bias = 0.3
for n in net.nodes:
    print(type(n.bias))
if net.links[0].input == gexnetpy.NULL_LINK:
    net.links[0].input = 0
    net.links[0].output = 1

net = None
net = gexnetpy.Network(1, 2)
net = None

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
