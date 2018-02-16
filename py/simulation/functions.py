import random


def set_scene(context):
    data = context.get('data')
    if data and callable(data):
        context['controller'].set_scene(data(context))


def set_random_seed(context):
    data = context.get('data')
    if data and callable(data):
        random.seed(data(context))
