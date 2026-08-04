from abc import ABC, abstractmethod


class BaseStateSerializer(ABC):

    @abstractmethod
    def serialize(self, data):
        pass


    @abstractmethod
    def deserialize(self, state):
        pass
    