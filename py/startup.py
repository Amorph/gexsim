import gexnetpy as GN

from nn.gnn import GNNet

G = GN.GNSystem()
nn = GNNet.create_random(G, 3, 1, 5)

for i in range(10):
    print(nn.process([0.5, 0.5, 0.5]))
    nn.back_propagate(0.15, [0.5])
print('--------------------------------')
for i in range(10):
    print(nn.process([0.75, 0.75, 0.75]))
    nn.back_propagate(0.15, [0.75])

import gym
import random
envs = [
    'CartPole-v0',
    'CartPole-v1',
    'MountainCar-v0',
    'MountainCarContinuous-v0',
    'Pendulum-v0',
    'Acrobot-v1'
]

env = gym.make(envs[2])
action = 0
env.reset()
while True:
    for _ in range(500):
        env.render()
        observation, reward, done, info = env.step(action)
        action = nn.process([observation[0], observation[1], reward])
        print(action)
        action = int((action[0] * + 1.0) / 2.0 + 0.5)
        # print(env.step(random.random()))# take a random action
    env.reset()
    nn = GNNet.create_random(G, 3, 1, 20)
exit(0)

import random
from threading import Thread

import time

'''
import gexnetpy as GN

G = GN.GNSystem()

test_links = [
    (0, 3),
    (1, 3),
    (2, 3),
    (3, 3),
    (3, 4),
    (3, 5),
    (5, 6),
    (4, 6),
    (3, 6)
]
links = G.create_stream_data(GN.GN_TYPE_LINK, test_links)
node_count = G.compute_node_count(links)
inputs, outputs = G.compute_in_out(links, node_count)
lock0 = inputs.lock(0, 0, 0)
lock1 = outputs.lock(0, 0, 0)
lock0.unlock()
lock1.unlock()

#stream = G.create_stream_data(GN.GN_TYPE_NUMBER, [1.5, 2.5, 3.5, 4.5, 5.5])
stream = G.create_stream_data(GN.GN_TYPE_INDEX, [1, 2, 3, 4, 5])
#stream = G.create_stream_data(GN.GN_TYPE_LINK, [(1, 2), (2, 3), (3, 4)])
lock = stream.lock(0, 0, 0)
for i in range(lock.count):
    lock.data[i] += 1
lock.unlock()
lock = stream.lock(0, 0, 0)


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
'''
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
    view.start_frame()
    simulation.update()
    simulation.draw(view)
    view.finish_frame()

view.destroy()
