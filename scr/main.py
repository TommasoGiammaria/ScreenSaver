#!/usr/bin/env python3
import sys, pygame, time, math, random
from pygame import Vector2
from curve_utils import *
from draw_utilities import *


black = 0, 0, 0
white = 255, 255, 255

gray = 128, 128, 128
dark_gray = 64, 64, 64
light_gray = 192, 192, 192

red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

yellow = 255, 255, 0
cyan = 0, 255, 255
magenta = 255, 0, 255

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

        self.screen_center = self.screen_size // 2
        self.circle_radius = info.current_h // 2 - 10

        if circle_radius is not None:
            self.circle_radius = circle_radius
    
        self.circle_width = circle_width
        self.curve_drawer = Curve_drawer()
        self.curve_generator = Curve_generator( self.screen_center, self.circle_radius )

        
        self.static_screen= pygame.display.set_mode(self.screen_size)
        self.dynamic_screen = pygame.display.set_mode(self.screen_size)

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
        # print(f"type(self.screen_size) : {type(self.screen_size)}")
        # print(f"type(self.screen_center) : {type(self.screen_center)}")
        # print(f"type(starting point initialization) : {type(self.curve_parameters['general_parameters']['starting_point'])}")


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

        # print(f'type (Last curve point 1): {type(curve_points[-1])}')
        # end_direction = curve_info['end_direction']

        # if strobo mode is True, draw the curve in segments
        for point_index in range(len(curve_points)-1):
            self.curve_drawer.draw_segment(
                (curve_points[point_index], curve_points[point_index+1]),
                self.drawing_parameters['segment_params'],
                self.dynamic_screen
            )
            self.update_display(blit_screen = True, draw_circle = False)
            time.sleep(0.05)

            # reset the screen each time we reach the strobo_tail number of segments
            if self.curve_drawer.segment_counter > self.drawing_parameters['strobo_tail'] and self.drawing_parameters['strobo']:
                self.curve_drawer.reset()
                self.static_screen.fill(black)
                self.update_display(blit_screen = False, draw_circle = True)

        # else:
        #     # draw the whole curve at once if not strobo mode
        #     self.curve_drawer.draw_curve(
        #         curve_points,
        #         self.drawing_parameters['segment_params'],
        #         self.dynamic_screen
        #     )

        time.sleep(0.01)        
        self.update_display(blit_screen = True, draw_circle = True)

        # print(f'type (Last curve point 2): {type(curve_points[-1])}')

        return curve_points[-1]



    def mainloop(self):
        """
        Main loop of the game
        """
        
        starting_angle = random.randint(0, 359)
        # print(f'Screen center: {self.screen_center}')
        # print(f'Circle radius: {self.circle_radius}')
        # print(f'Starting angle: {starting_angle}')
        starting_point = point_in_circle( self.screen_center, self.circle_radius, starting_angle )
        
        # print(f"type(starting point main loop 1) : {type(starting_point)}")
        # print(f'Starting point (main loop): {starting_point}')
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
            start_line_length = 10
            next_point = point_in_circle( starting_point, start_line_length, direction )
            starting_point = next_point
        
            # print(f"type(starting point main loop 2) : {type(starting_point)}")



                
            self.curve_parameters['general_parameters']['starting_point'] = starting_point
            self.curve_parameters['general_parameters']['starting_direction'] = direction

            # print(f"type(starting point main loop 3) : {type(starting_point)}")

            endpoint = self.generate_single_curve(randomgen = True)
            
            # print(f"type(endpoint main loop) : {type(endpoint)}")

            
            toward_circle_center = 180 + direction
            if toward_circle_center > 360: toward_circle_center -= 360

            starting_point = endpoint
            direction = toward_circle_center
            # print(f"type(starting point main loop 4) : {type(starting_point)}")

            time.sleep(0.5)


if __name__ == "__main__":
    game = Game_engine()
    game.initialize_screen()
    game.mainloop()
    

