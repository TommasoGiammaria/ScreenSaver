#!/usr/bin/env python3
import pygame, math, random
from typing import Dict, List, Tuple, Union
# from typing import Dict, List, Tuple, Set, Callable, Any
from pygame import Vector2

"""
This module contains simple functions to draw curves with the pygame module.
The curves are tuples of points, and the curves are drawn as straight lines between the points.
The class is meant to be used with the tuples of points created with the Curve_generator class.
"""


class Curve_drawer:
    """
    Class to draw curves inside a circle
    """
    default_segment_parameters = {
        'color'         : "white",
        'line_width'    : 1
    }

    
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
            segment_params = default_segment_parameters,
            screen : pygame.Surface = None
        ) -> None:
        """
        draw a single (straight) segment
        """
        self.segment_counter += 1
        # print(type(points[0]), type(points[1]))
        self.tracked_length += math.sqrt((points[1].x - points[0].x)**2 + (points[1].y - points[0].y)**2)
        if segment_params['line_width'] == 1:
            pygame.draw.aaline(screen, segment_params['color'], points[0], points[1])
        else:
            pygame.draw.line(screen, segment_params['color'], points[0], points[1], width = segment_params['line_width'])


    def draw_curve(
            self,
            points : Tuple[Vector2] = (Vector2(0, 0), Vector2(1, 1), Vector2(2, 2)),
            segment_params = default_segment_parameters,
            screen : pygame.Surface = None
        ) -> None:
        """
        draw a single curve, kwargs are passed to draw_segment as keyword arguments
        """
        for i in range(len(points)-2):
            self.draw_segment((points[i], points[i+1]), segment_params, screen)

