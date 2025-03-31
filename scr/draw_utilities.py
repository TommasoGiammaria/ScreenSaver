#!/usr/bin/env python3
import pygame, math, random
from typing import Dict, List, Tuple, Union
# from typing import Dict, List, Tuple, Set, Callable, Any
from pygame import Vector2

"""
This module contains simple functions to generate random curves inside a circle.
The curves can be of three different types (0, 1, 2).
The program can be used to generate random patterns that can be used as background for other projects.
"""



class Curve_drawer:
    """
    Class to draw curves inside a circle
    """
    def __init__(
            self,
        ):
        self.segment_counter = 0
        self.tracked_length = 0

    def reset(self):
        """
        Reset the curve drawer
        """
        self.segment_counter = 0
        self.tracked_length = 0


    def draw_segment(
            self,
            points : Tuple[Vector2, Vector2] = (Vector2(0, 0), Vector2(1, 1)),
            color : str = 'white',
            line_width : int = 1,
            screen : pygame.Surface = None
        ) -> None:
        """
        draw a single (straight) segment
        """
        self.segment_counter += 1
        self.tracked_length += math.sqrt((points[1].x - points[0].x)**2 + (points[1].y - points[0].y)**2)
        if line_width == 1:
            pygame.draw.aaline(screen, color, points[0], points[1])
        else:
            pygame.draw.line(screen, color, points[0], points[1], width = line_width)



    def draw_curve(
            self,
            points : Tuple[Vector2] = (Vector2(0, 0), Vector2(1, 1), Vector2(2, 2)),
            **kwargs
        ) -> None:
        """
        draw a single curve, kwargs are passed to draw_segment as keyword arguments
        """
        for i in range(len(points)-2):
            self.draw_segment((points[i], points[i+1]), **kwargs)

