import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
from numpy import ndarray

jsonpickle_numpy.register_handlers()


class Descriptor:

    def __init__(self, lbph: ndarray):
        self.lbph = lbph

    lbph: ndarray

    def to_json(self) -> dict:
        return {
            "lbph": jsonpickle.encode(self.lbph)
        }

    @staticmethod
    def from_json(data: dict):
        return Descriptor(jsonpickle.decode(data['lbph']))
