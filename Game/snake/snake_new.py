import pygame
from collections import namedtuple


body = namedtuple('body', 'type x_coord y_coord')

class snake:
    def __init__(self):
        self.__snake =