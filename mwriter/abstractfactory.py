from abc import ABC, abstractmethod

"""
#################################################################################
Class MLDataSet: simple Factory Method Product pattern wrapper 

Instance variables:
   X: network ready input data representation (some matrix)
   Y: network ready label data representation (some matrix)                   """

class MLDataSet:
#{
    def __init__(self, X, Y):
    #{
        self.X = X
        self.Y = Y
    #}
#}

"""
#################################################################################
Class MLDataCreator: Abstract Class (ABC) implementation Abstract Factory pattern

Instance variables:
   _datasets: dictionary of <name : MLDataSet> pairs (implied 'protected')

Abstract methods:
   create_dataset(name): Creator method of Factory Method pattern
      arg: ds_name - identifier/dictionary key of the specific MLDataSet
      arg: input_file - list of filenames of the input data files
      return: MLDataSet object being stored in _datasets                 """

class MLDataFactory(ABC):
#{
    def __init__(self):
    #{  
        super().__init__()
        self._datasets = {}
    #}
    
    @abstractmethod
    def create_dataset(self, ds_name, input_files): pass
#}
