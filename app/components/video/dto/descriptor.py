import jsonpickle.ext.numpy as jsonpickle_numpy
from numpy import ndarray

jsonpickle_numpy.register_handlers()


class Descriptor:

    def __init__(self, features: ndarray):
        self.features = features

    features: ndarray
