#!/usr/bin/env python3
import sys, pygame, time, math, random
from pygame import Vector2
from scr.curve_utils import *
from scr.draw_utilities import *


black = 0, 0, 0
white = 255, 255, 255
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
yellow = 255, 255, 0
cyan = 0, 255, 255
magenta = 255, 0, 255
gray = 128, 128, 128
dark_gray = 64, 64, 64
light_gray = 192, 192, 192

class Game_engine:
    """
    Class to handle the pygame display and the game loop
    """
    

    def __init__(
            self,
            screen_size : Vector2 = None,
            circle_radius : int = None,
            circle_width : int = 5,
            fullscreen : bool = True
        ):

        # os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
                
        info = pygame.display.Info()
        self.screen_size = Vector2(info.current_w, info.current_h)
        self.circle_color = gray
        self.background_color = black

        if screen_size is not None: 
            self.screen_size = screen_size

        self.screen_center = screen_size // 2
        self.circle_radius = info.current_h // 2 - 10

        if circle_radius is not None:
            self.circle_radius = circle_radius
    
        self.circle_width = circle_width
        self.curve_drawer = Curve_drawer()
        self.curve_generator = Curve_generator( self.screen_center, self.circle_radius )

        
        self.static_screen= pygame.display.set_mode(screen_size)
        self.dynamic_screen = pygame.display.set_mode(screen_size)

        if fullscreen:
            pygame.display.toggle_fullscreen()
        
                
        self.current_mouse_position = pygame.mouse.get_pos()
        self.previous_mouse_position = pygame.mouse.get_pos()

        self.curve_counter = 0

        self.drawing_parameters = {
            'strobo'            : False,
            'strobo_tail'       : 50,
            'segment_params'    : Curve_drawer.default_segment_parameters
        }

        self.curve_parameters = {
            'general_parameters': Curve_generator.default_general_params,
            'circle_parameters': Curve_generator.default_circle_params,       
            'ellipse_parameters': Curve_generator.default_ellipse_params
        }


    def update_parameters(
            self,
            curvedict : dict = {},
            drawdict : dict = {}
        ) -> bool:
        """
        Update the parameters of the game.
        Returns True if the parameters were updated, False otherwise.
        """
        for key, value in curvedict.items():
            if key in self.curve_parameters:
                self.curve_parameters[key] = value
            else:
                print(f"Unknown curve parameter: {key}")
                return False

        for key, value in drawdict.items():
            if key in self.drawing_parameters:
                self.drawing_parameters[key] = value
            else:
                print(f"Unknown draw parameter: {key}")
                return False
        
        return True


    def update_display(self, blit_screen = True, draw_circle = True):
        """
        Update the display
        """
        if draw_circle:
            # draw a circle in the middle of the screen
            pygame.draw.circle(surface = self.static_screen, color = self.circle_color, center = self.screen_center, radius = self.circle_radius, width = self.circle_width)

            # if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)

            # draw another circle to fill the space outside this circle
            pygame.draw.circle(surface = self.static_screen, color = self.background_color, center = self.screen_center, radius = self.circle_radius + 2000, width = 2000)

        if blit_screen:
            self.dynamic_screen.blit(self.static_screen, (0,0))
        pygame.display.flip()


    def initialize_screen(self):
        """
        Initialize the screen
        """
        # fill a black screen
        self.static_screen.fill(black)
    
        # and update the display
        self.update_display(blit_screen = False)
    
    
    def check_mouse(self):
        """
        Check if the mouse is moving
        """
        self.current_mouse_position = pygame.mouse.get_pos()
        if self.current_mouse_position != self.previous_mouse_position: sys.exit()
        self.previous_mouse_position = self.current_mouse_position


    def check_pressed_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


    def generate_single_curve(
            self,
            randomgen = False,
            name = 'circle'
        ) -> Vector2:
        """
        Generate a single curve.
        If randomgen is True, then the function will generate random parameters for the curve
        (and ignore the rest of the arguments)
        """
        self.curve_counter += 1

        if name == 'circle':
            this_curve_dict = self.curve_parameters['circle_parameters']
        elif name == 'ellipse':
            this_curve_dict = self.curve_parameters['ellipse_parameters']
        else:
            print(f"Unknown curve type {name}")
            return Vector2(0, 0)
    
        curve_info = self.curve_generator.generate_curve(
            randomgen,
            name,
            self.curve_parameters['general_parameters'],
            this_curve_dict
        )

        curve_points = curve_info['points']
        # end_direction = curve_info['end_direction']

        if self.drawing_parameters['strobo']:
            # if strobo mode is True, draw the curve in segments
            for point_index in range(len(curve_points)-1):
                self.curve_drawer.draw_segment(
                    (curve_points[point_index], curve_points[point_index+1]),
                    self.drawing_parameters['segment_params'],
                    self.dynamic_screen
                )
                self.update_display(blit_screen = True, draw_circle = False)
                time.sleep(0.01)

                # reset the screen each time we reach the strobo_tail number of segments
                if self.curve_drawer.segment_counter > self.drawing_parameters['strobo_tail']:
                    self.curve_drawer.reset()
                    self.static_screen.fill(black)
                    self.update_display(blit_screen = False, draw_circle = True)

        else:
            # draw the whole curve at once if not strobo mode
            self.curve_drawer.draw_curve(
                curve_points,
                self.drawing_parameters['segment_params'],
                self.dynamic_screen
            )

        time.sleep(0.01)        
        self.update_display(blit_screen = True, draw_circle = True)

        return curve_points[-1]



    def mainloop(self):
        """
        Main loop of the game
        """
        
        starting_angle = random.randint(0, 359)
        starting_point = point_in_circle( self.screen_center, self.circle_radius, starting_angle )
        toward_circle_center = 180 + starting_angle
        if toward_circle_center > 360: toward_circle_center -= 360
        direction = toward_circle_center


        while True:
            self.check_mouse()
            self.check_pressed_keys()

            if self.curve_counter > 30:
                self.static_screen.fill(black)
                self.dynamic_screen.fill(black)
                self.update_display(blit_screen = True, draw_circle = True)
                self.curve_counter = 0

            # completely random color
            brighter_color_index = random.randint(0, 2)
            linecolor = [random.randint(0, 250), random.randint(0, 250), random.randint(0, 250)]
            linecolor[brighter_color_index] = 250
            self.background_color = [ linecolor[0] // 2, linecolor[1] // 2, linecolor[2] // 2]
            self.circle_color = linecolor
            self.drawing_parameters['segment_params']['color'] = linecolor

            # self.drawing_parameters['segment_params']['line_width'] = random.randint(0, 2)

            
            self.update_display(blit_screen = False, draw_circle = True)

            # initialize internal parameters
            # the starting direction is from the starting point to the center of the circle
            start_line_length = 30
            next_point = point_in_circle( self.screen_center, start_line_length, direction )
            starting_point = next_point

                
            self.curve_parameters['general_parameters']['starting_point'] = starting_point
            self.curve_parameters['starting_direction']['starting_direction'] = direction

            endpoint = self.generate_single_curve(randomgen = True)

            
            toward_circle_center = 180 + direction
            if toward_circle_center > 360: toward_circle_center -= 360
                
            self.curve_parameters['general_parameters']['starting_point'] = endpoint
            self.curve_parameters['starting_direction']['starting_direction'] = toward_circle_center

            


            # inside_circle = True
            # start_straight = False
            # while inside_circle:
            #     if inside_circle:            
            #         prev_tracked_length = tracked_length
            #         curve_type = curve_types[random.randint(0, 2)]
            #         end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
            #         tracked_length += length
            #         next_point = end_point
            #         direction = end_direction
            #         curve_type = curve_types[random.randint(0, 2)]
            #         left_right = -left_right
            #         end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
            #         tracked_length += length
            #         next_point = end_point
            #         direction = end_direction
            #         if tracked_length > 15*circle_radius:
            #             inside_circle = False
            #         if tracked_length == prev_tracked_length:
            #             inside_circle = False
            #             starting_angle = random.randint(0, 359)
            #             starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
            #             # start with a random point inside the circle
            #             toward_circle_center = 180 + starting_angle
            #             if toward_circle_center > 360: toward_circle_center -= 360
            #             direction = toward_circle_center

            # starting_point = next_point
            # direction = direction - 180
            # starting_point = point_in_circle( next_point, 2, direction )
            # starting_point = next_point

            
            # if randomgen:
            #     starting_angle = random.randint(0, 359)
            #     starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
            #     # start with a random point inside the circle
            #     toward_circle_center = 180 + starting_angle
            #     if toward_circle_center > 360: toward_circle_center -= 360
            #     direction = toward_circle_center

            
            
            # screen2.blit(screen, (0,0))
            # pygame.draw.circle(surface = screen, color = linecolor, center = screen_center, radius = circle_radius, width = circle_width)
            # if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)
            # else: pygame.draw.circle(surface = screen, color = background_color, center = screen_center, radius = circle_radius + 2000, width = 2000)
            
            # pygame.display.flip()


# info = pygame.display.Info()
# screen_size = Vector2(info.current_w, info.current_h)
# screen_center = screen_size // 2
# circle_radius = info.current_h // 2 - 10
# circle_width = 5
# black = 0, 0, 0
# self.curve_counter = 0
# segment_counter = 0


# screen = pygame.display.set_mode(screen_size)
# screen2 = pygame.display.set_mode(screen_size)

# pygame.display.toggle_fullscreen()



# max_deflection = random.randint(3, 5)
# max_angle = random.randint(30, 90)
# max_displacement = random.randint(5, 15)
# strobo = True if random.randint(0, 1) == 1 else False
# randomgen = True if random.randint(0, 1) == 1 else False
# strobo_tail = 100
# curve_pool = [[0, 1, 2], [0, 0, 0], [1, 1, 1], [2, 2, 2], [0, 1, 0], [0, 2, 0]]
# curve_types = curve_pool[random.randint(0, len(curve_pool) - 1)]
# linetype = 0
# # # linetype = random.randint(0, 2)
# # current_mouse_position = pygame.mouse.get_pos()
# # previous_mouse_position = pygame.mouse.get_pos()


# def reinizialize():
#     global max_deflection, max_angle, max_displacement, strobo, randomgen, segment_counter, curve_types, linetype
#     max_deflection = random.randint(3, 5)
#     max_angle = random.randint(30, 90)
#     max_displacement = random.randint(5, 15)
#     strobo = True if random.randint(0, 1) == 1 else False
#     randomgen = True if random.randint(0, 1) == 1 else False
#     segment_counter = 0
#     curve_types = curve_pool[random.randint(0, len(curve_pool) - 1)]
#     # linetype = random.randint(0, 2)


# def update_inputs():
#     global current_mouse_position, previous_mouse_position
#     current_mouse_position = pygame.mouse.get_pos()
#     if current_mouse_position != previous_mouse_position: sys.exit()
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT: sys.exit()
#     previous_mouse_position = current_mouse_position


# def rad_to_deg(angle = math.pi): return (angle*180)/math.pi


# def switch_to_circle_coordinates(old_coordinates = Vector2(0, 0)):
#     translated_coordinates = old_coordinates - screen_center
#     polar_angle = rad_to_deg(math.tan(abs(translated_coordinates.y/translated_coordinates.x)))
#     if translated_coordinates.y < 0:
#         if translated_coordinates.x > 0: polar_angle = 360 - polar_angle
#         else: polar_angle += 180
#     elif translated_coordinates.x < 0: polar_angle = 180 - polar_angle
#     rotated_coordinates = Vector2( math.sqrt(translated_coordinates.x**2 + translated_coordinates.y**2), polar_angle)
#     return rotated_coordinates


# def point_in_circle(center = screen_center, radius = circle_radius, angle = 0): return center + Vector2.from_polar((radius, -angle))


# def isin_circle(center = screen_center, radius = circle_radius, point_position = Vector2(0, 0)): return (center.x - point_position.x)**2 + (center.y - point_position.y)**2 < radius**2


# def drawline(starting_point = Vector2(0, 0), next_point = Vector2(0, 0), color = 'white'):
#     global segment_counter, strobo_tail, linetype
#     if strobo:
#         segment_counter = segment_counter + 1 if segment_counter < strobo_tail else 0
#         if segment_counter == strobo_tail:
#             screen.fill(black)
#             pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)
#     else: time.sleep(0.01)
#     update_inputs()
#     if linetype == 0: pygame.draw.aaline(screen2, color, starting_point, next_point, True)
#     elif linetype == 1: pygame.draw.line(screen2, color, starting_point, next_point, width = 2)
#     elif linetype == 2: pygame.draw.line(screen2, color, starting_point, next_point, width = 3)
#     screen2.blit(screen, (0,0))
#     pygame.display.flip()


# # simple function to draw curves of different types [0, 1, 2]
# def draw_random_curve(type = 0, starting_point = Vector2(0, 0),  starting_direction = 0, left_right = -1, color = 'white'):
#     tracked_length = 0
#     direction = starting_direction
#     next_point = starting_point
#     if type == 0:
#         # simple curve with fixed deflection and deflection/displacement ratio
#         deflection = random.randint(0, max_deflection)
#         deflection_to_displacement_ratio = random.randint(2, max_displacement)
#         deflection = left_right*deflection
#         for i in range(50):
#             if isin_circle(screen_center, circle_radius, next_point):
#                 direction += deflection
#                 next_point = point_in_circle( starting_point, deflection_to_displacement_ratio, direction )
#                 drawline(starting_point, next_point, color )
#                 tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
#                 starting_point = next_point
#             else: return next_point, direction, False, tracked_length
#     elif type > 0:
#         # another (more ellyptical) curve (to make more strong curves)
#         # and displacement increase/decrease step
#         deflection = random.randint(0, max_deflection - 1)
#         deflection = 0
#         deflection = left_right*deflection
#         min_displacement_value = random.randint(1, max_displacement // 2)
#         counter = 0
#         single_displacement = random.randint(10, 30)
#         while single_displacement > min_displacement_value and deflection < max_angle:
#             single_displacement -= min_displacement_value
#             if isin_circle(screen_center, circle_radius, next_point):
#                 deflection += left_right
#                 counter += 1
#                 direction += deflection
#                 next_point = point_in_circle( starting_point, single_displacement, direction)
#                 drawline( starting_point, next_point, color )
#                 tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
#                 starting_point = next_point
#             else: return next_point, direction, False, tracked_length
#         if type > 1:
#             # if type 3, close the half ellypsis
#             for i in range(counter - 1):
#                 if isin_circle(screen_center, circle_radius, next_point):
#                     deflection -= left_right
#                     single_displacement += min_displacement_value
#                     direction += deflection
#                     next_point = point_in_circle( starting_point, single_displacement, direction)
#                     drawline( starting_point, next_point, color )
#                     tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
#                     starting_point = next_point                
#                 else: return next_point, direction, False, tracked_length

#     return next_point, direction, True, tracked_length


# starting_angle = random.randint(0, 359)
# starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
# toward_circle_center = 180 + starting_angle
# if toward_circle_center > 360: toward_circle_center -= 360
# direction = toward_circle_center


# fill the screen in black
# screen.fill(black)
# pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)



# while True:

#     # reset screen if more than 30 lines
#     if self.curve_counter > 30:
#         reinizialize()
#         screen.fill(black)
#         pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)
#         self.curve_counter = 0


#     update_inputs()


#     self.curve_counter += 1

#     # completely random color
#     brighter_color_index = random.randint(0, 2)
#     linecolor = [random.randint(0, 250), random.randint(0, 250), random.randint(0, 250)]
#     linecolor[brighter_color_index] = 250
#     background_color = [ linecolor[0] // 2, linecolor[1] // 2, linecolor[2] // 2]

#     # random linetype
#     # linetype = random.randint(0, 2)


#     # initialize internal parameters
#     # starting_deflection = random.randint(0, 15)             # starting deflection
#     left_right = 1 - random.randint(0, 1)*2        # starting direction (left/right)
#     # the starting direction is from the starting point to the center of the circle
#     start_line_length = 20
#     tracked_length = start_line_length
#     next_point = point_in_circle( starting_point, start_line_length, direction )
#     pygame.draw.line(screen, linecolor, starting_point, next_point)
#     pygame.draw.circle(surface = screen, color = linecolor, center = screen_center, radius = circle_radius, width = circle_width)
#     if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)
#     else: pygame.draw.circle(surface = screen, color = background_color, center = screen_center, radius = circle_radius + 2000, width = 2000)

#     inside_circle = True
#     start_straight = False
#     while inside_circle:
#         if inside_circle:            
#             prev_tracked_length = tracked_length
#             curve_type = curve_types[random.randint(0, 2)]
#             end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
#             tracked_length += length
#             next_point = end_point
#             direction = end_direction
#             curve_type = curve_types[random.randint(0, 2)]
#             left_right = -left_right
#             end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
#             tracked_length += length
#             next_point = end_point
#             direction = end_direction
#             if tracked_length > 15*circle_radius:
#                 inside_circle = False
#             if tracked_length == prev_tracked_length:
#                 inside_circle = False
#                 starting_angle = random.randint(0, 359)
#                 starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
#                 # start with a random point inside the circle
#                 toward_circle_center = 180 + starting_angle
#                 if toward_circle_center > 360: toward_circle_center -= 360
#                 direction = toward_circle_center

#     # starting_point = next_point
#     direction = direction - 180
#     starting_point = point_in_circle( next_point, 2, direction )
#     # starting_point = next_point

    
#     if randomgen:
#         starting_angle = random.randint(0, 359)
#         starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
#         # start with a random point inside the circle
#         toward_circle_center = 180 + starting_angle
#         if toward_circle_center > 360: toward_circle_center -= 360
#         direction = toward_circle_center

    
    
#     screen2.blit(screen, (0,0))
#     pygame.draw.circle(surface = screen, color = linecolor, center = screen_center, radius = circle_radius, width = circle_width)
#     if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)
#     else: pygame.draw.circle(surface = screen, color = background_color, center = screen_center, radius = circle_radius + 2000, width = 2000)
    
#     pygame.display.flip()
