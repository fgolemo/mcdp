# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class NotBelongs(Exception):
    pass


class Space():
    __metaclass__ = ABCMeta
#
#     @abstractmethod
#     def get_name(self):
#         pass
#
#     @abstractmethod
#     def get_units(self):
#         pass
#
#     @abstractmethod
#     def get_comment(self):
#         pass

    def format(self, x):
        """ Formats a point in the space. """
        return x.__repr__()

    @abstractmethod
    def belongs(self, x):
        pass
