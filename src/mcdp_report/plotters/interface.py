# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from contracts import contract


class NotPlottable(Exception):
    pass

class Plotter():
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_plot_space(self, space):
        pass

    @abstractmethod
    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        pass

    @abstractmethod
    def plot(self, pylab, axis, space, value, params={}):
        pass

    def get_xylabels(self, _space):
        return None, None