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

def rad_to_deg(angle : float = math.pi) -> float: return (angle*180)/math.pi


def switch_to_local_coordinates(
        old_coordinates : Vector2 = Vector2(0, 0),
        center : Vector2 = Vector2(0, 0)
    ) -> Vector2:
    """
    switch from the linear (default) coordinates to polar coordinates w.r.t. the circle's center
    """
    translated_coordinates = old_coordinates - center
    polar_angle = rad_to_deg(math.tan(abs(translated_coordinates.y/translated_coordinates.x)))
    if translated_coordinates.y < 0:
        if translated_coordinates.x > 0: polar_angle = 360 - polar_angle
        else: polar_angle += 180
    elif translated_coordinates.x < 0: polar_angle = 180 - polar_angle
    rotated_coordinates = Vector2( math.sqrt(translated_coordinates.x**2 + translated_coordinates.y**2), polar_angle)
    return rotated_coordinates


def point_in_circle(
        center : Vector2 = Vector2(0, 0),
        radius : float = 20.0,
        angle : float = 0.0
    ) -> Vector2:
    """
    return the coordinates of a point inside a circle given the center, the radius and the angle.
    This would be the polar coordinates of the point (i.e. the inverse transformation w.r.t. the previous function)
    """
    return center + Vector2.from_polar((radius, -angle))


def isin_circle(
        center : Vector2 = Vector2(0, 0),
        radius : float = 20.0,
        point_position : Vector2 = Vector2(0, 0)
    ) -> bool:
    """
    check if a point is inside a circle of certain radius and center
    """
    return (center.x - point_position.x)**2 + (center.y - point_position.y)**2 < radius**2



class Curve_generator:
    """
    Class to generate curves inside a circle
    """
    default_general_params = {
        'starting_point'        : Vector2(0, 0),
        'starting_direction'    : 0,
        'left_right'            : -1,
    }
    default_circle_params = {
        'deflection'                    : 1,
        'displacement_deflection_ratio' : 2,
        'n_steps'                       : 2
    }
    default_ellipse_params = {
        'max_deflection'        : 1,
        'displacement_range'    : (1, 4, 1),
        'closed'                : True
    }

    def __init__(
            self,            
            screen_center : Vector2 = Vector2(0,0),
            circle_radius : float = 0.
        ):
        self.screen_center = screen_center
        self.circle_radius = circle_radius


    def generate_circle(
            self,
            gen_params : Dict[str, Union[Vector2, int]] = default_general_params,
            curve_params : Dict[str, int] = default_circle_params
        ) -> Dict[str, Union[Tuple[int], int]]:
        """
        draws an arc of a circle, starting from a point and pointing to a direction.
        The arc is generated as a set of VEctor2 points, but it is NOT drawn.
        The circle is not defined by radius and angle, but by deflection and displacement-per-single-deflection (or displacement/deflection ratio)
        The length of the arc is defined by the number of steps (n_steps key).
        Returns the curve points and the end direction.
        """
        deflection = gen_params['left_right']*curve_params['deflection']
        displacement_deflection_ratio = curve_params['displacement_deflection_ratio']
        starting_point = gen_params['starting_point']
        next_point = gen_params['starting_point']
        direction = gen_params['starting_direction']
        curve_points = (starting_point,)
        
        for i in range(curve_params['n_steps']):
            if isin_circle(self.screen_center, self.circle_radius, next_point):
                direction += deflection

                next_point = point_in_circle(
                    starting_point,
                    displacement_deflection_ratio,
                    direction
                )
                starting_point = next_point
                curve_points += (next_point,)
            else:
                return {
                    'points'        : curve_points,
                    'end_direction' : direction,
                }

        return {
            'points'        : curve_points,
            'end_direction' : direction,
        }


    def generate_ellipse(
            self,
            gen_params : Dict[str, Union[Vector2, int]] = default_general_params,
            curve_params : Dict[str, Union[Tuple[int, int, int], int, bool]] = default_ellipse_params
        ) -> Dict[str, Union[Tuple[int], int]]:
        """
        draw an elliptical (? I have to do some math... ) arc, similar to circle but with different curve_params dict.
        In this case the direction is changed at each step by "deflection", but deflection increases at each step.
        The arc ends when one of the following conditions occurs:
        - the displacement value reaches its min
        - the deflection value reaches its max
        If we have to draw also the second half, then we start lowering the deflection once it gets the max value.
        Also the displacement decreases increasing the deflection, then returns to the initial value at the end.
        The arc is generated as a set of VEctor2 points, but it is NOT drawn.
        Returns the curve points and the end direction.
        """
        max_deflection = curve_params['max_deflection']
        deflection = 0
        # max_deflection = gen_params['left_right']*curve_params['deflection']
        starting_displacement = curve_params['displacement_range'][1]
        min_displacement = curve_params['displacement_range'][0]
        delta_displacement = curve_params['displacement_range'][2]
        starting_point = gen_params['starting_point']
        next_point = gen_params['starting_point']
        direction = gen_params['starting_direction']


        counter = 0
        curve_points = (starting_point)
        single_displacement = starting_displacement
        while single_displacement > min_displacement and deflection < max_deflection:
            single_displacement -= delta_displacement
            if isin_circle( self.screen_center, self.circle_radius, next_point):
                deflection += 1
                counter += 1
                direction += gen_params['left_right']*deflection

                next_point = point_in_circle(
                    starting_point,
                    single_displacement,
                    direction
                )
                
                starting_point = next_point
                curve_points += (next_point,)
            else:
                return  {
                    'points'        : curve_points,
                    'end_direction' : direction,
                }
            if curve_params['closed']:
                # this part draws the second half of the ellipsis
                for i in range(counter - 1):
                    if isin_circle( self.screen_center, self.circle_radius, next_point):
                        deflection -= 1
                        single_displacement += delta_displacement
                        direction -= gen_params['left_right']*deflection

                        next_point = point_in_circle(
                            starting_point,
                            single_displacement,
                            direction
                        )
                        
                        starting_point = next_point
                        curve_points += (next_point,)
                    else:
                        return  {
                            'points'        : curve_points,
                            'end_direction' : direction,
                        }
        return  {
            'points'        : curve_points,
            'end_direction' : direction,
        }


    def generate_curve(
            self,
            randomgen = False,
            name = 'circle',
            general_parameters = default_general_params,
            curve_parameters = default_circle_params
        ) -> Dict[str, Union[Tuple[int], int]]:
        """
        this function is a general drawing method, choose the function with the "name" variable
        If "randomgen" is True, then the function will generate random parameters for the curve (and ignore the rest of the arguments)
        The curve is generated as a set of VEctor2 points, but it is NOT drawn.
        """
        random_circle_params = {
            'deflection'                    : random.randint(1, 5),
            'displacement_deflection_ratio' : random.randint(3, 10),
            'n_steps'                       : random.randint(30, 70),
        }
        random_ellipse_params = {
            'max_deflection'        : random.randint(1, 5),
            'displacement_range'    : (random.randint(20, 50), random.randint(4, 7), random.randint(1, 2)),
            'closed'                : random.choice([True, False])
        }
        if randomgen:
            general_parameters['left_right'] = random.randint(-1, 1)
            name = random.choice(['circle', 'ellipse'])
            if name == 'circle':
                curve_parameters = random_circle_params
            elif name == 'ellipse':
                curve_parameters = random_ellipse_params

        if name == 'circle':
            curvedict = self.generate_circle(
                general_parameters,
                curve_parameters,
            )
        if name == 'ellipse':
            curvedict = self.generate_ellipse(
                general_parameters,
                curve_parameters,
            )

        return curvedict