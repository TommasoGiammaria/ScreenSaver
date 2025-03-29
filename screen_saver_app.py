#!/usr/bin/env python3
import sys, pygame, time, math, random
from pygame import Vector2
from .draw_utils import *

# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()


info = pygame.display.Info()
screen_size = Vector2(info.current_w, info.current_h)
screen_center = screen_size // 2
circle_radius = info.current_h // 2 - 10
circle_width = 5
black = 0, 0, 0
line_counter = 0
segment_counter = 0


screen = pygame.display.set_mode(screen_size)
screen2 = pygame.display.set_mode(screen_size)

pygame.display.toggle_fullscreen()

max_deflection = random.randint(3, 5)
max_angle = random.randint(30, 90)
max_displacement = random.randint(5, 15)
strobo = True if random.randint(0, 1) == 1 else False
randomgen = True if random.randint(0, 1) == 1 else False
strobo_tail = 100
curve_pool = [[0, 1, 2], [0, 0, 0], [1, 1, 1], [2, 2, 2], [0, 1, 0], [0, 2, 0]]
curve_types = curve_pool[random.randint(0, len(curve_pool) - 1)]
linetype = 0
# linetype = random.randint(0, 2)
current_mouse_position = pygame.mouse.get_pos()
previous_mouse_position = pygame.mouse.get_pos()

def reinizialize():
    global max_deflection, max_angle, max_displacement, strobo, randomgen, segment_counter, curve_types, linetype
    max_deflection = random.randint(3, 5)
    max_angle = random.randint(30, 90)
    max_displacement = random.randint(5, 15)
    strobo = True if random.randint(0, 1) == 1 else False
    randomgen = True if random.randint(0, 1) == 1 else False
    segment_counter = 0
    curve_types = curve_pool[random.randint(0, len(curve_pool) - 1)]
    # linetype = random.randint(0, 2)

def update_inputs():
    global current_mouse_position, previous_mouse_position
    current_mouse_position = pygame.mouse.get_pos()
    if current_mouse_position != previous_mouse_position: sys.exit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    previous_mouse_position = current_mouse_position


def rad_to_deg(angle = math.pi): return (angle*180)/math.pi

def switch_to_circle_coordinates(old_coordinates = Vector2(0, 0)):
    translated_coordinates = old_coordinates - screen_center
    polar_angle = rad_to_deg(math.tan(abs(translated_coordinates.y/translated_coordinates.x)))
    if translated_coordinates.y < 0:
        if translated_coordinates.x > 0: polar_angle = 360 - polar_angle
        else: polar_angle += 180
    elif translated_coordinates.x < 0: polar_angle = 180 - polar_angle
    rotated_coordinates = Vector2( math.sqrt(translated_coordinates.x**2 + translated_coordinates.y**2), polar_angle)
    return rotated_coordinates

def point_in_circle(center = screen_center, radius = circle_radius, angle = 0): return center + Vector2.from_polar((radius, -angle))

def isin_circle(center = screen_center, radius = circle_radius, point_position = Vector2(0, 0)): return (center.x - point_position.x)**2 + (center.y - point_position.y)**2 < radius**2

def drawline(starting_point = Vector2(0, 0), next_point = Vector2(0, 0), color = 'white'):
    global segment_counter, strobo_tail, linetype
    if strobo:
        segment_counter = segment_counter + 1 if segment_counter < strobo_tail else 0
        if segment_counter == strobo_tail:
            screen.fill(black)
            pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)
    else: time.sleep(0.01)
    update_inputs()
    if linetype == 0: pygame.draw.aaline(screen2, color, starting_point, next_point, True)
    elif linetype == 1: pygame.draw.line(screen2, color, starting_point, next_point, width = 2)
    elif linetype == 2: pygame.draw.line(screen2, color, starting_point, next_point, width = 3)
    screen2.blit(screen, (0,0))
    pygame.display.flip()

# simple function to draw curves of different types [0, 1, 2]
def draw_random_curve(type = 0, starting_point = Vector2(0, 0),  starting_direction = 0, left_right = -1, color = 'white'):
    tracked_length = 0
    direction = starting_direction
    next_point = starting_point
    if type == 0:
        # simple curve with fixed deflection and deflection/displacement ratio
        deflection = random.randint(0, max_deflection)
        deflection_to_displacement_ratio = random.randint(2, max_displacement)
        deflection = left_right*deflection
        for i in range(50):
            if isin_circle(screen_center, circle_radius, next_point):
                direction += deflection
                next_point = point_in_circle( starting_point, deflection_to_displacement_ratio, direction )
                drawline(starting_point, next_point, color )
                tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
                starting_point = next_point
            else: return next_point, direction, False, tracked_length
    elif type > 0:
        # another (more ellyptical) curve (to make more strong curves)
        # and displacement increase/decrease step
        deflection = random.randint(0, max_deflection - 1)
        deflection = 0
        deflection = left_right*deflection
        min_displacement_value = random.randint(1, max_displacement // 2)
        counter = 0
        single_displacement = random.randint(10, 30)
        while single_displacement > min_displacement_value and deflection < max_angle:
            single_displacement -= min_displacement_value
            if isin_circle(screen_center, circle_radius, next_point):
                deflection += left_right
                counter += 1
                direction += deflection
                next_point = point_in_circle( starting_point, single_displacement, direction)
                drawline( starting_point, next_point, color )
                tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
                starting_point = next_point
            else: return next_point, direction, False, tracked_length
        if type > 1:
            # if type 3, close the half ellypsis
            for i in range(counter - 1):
                if isin_circle(screen_center, circle_radius, next_point):
                    deflection -= left_right
                    single_displacement += min_displacement_value
                    direction += deflection
                    next_point = point_in_circle( starting_point, single_displacement, direction)
                    drawline( starting_point, next_point, color )
                    tracked_length += math.sqrt((next_point.x - starting_point.x)**2 + (next_point.y - starting_point.y)**2)
                    starting_point = next_point                
                else: return next_point, direction, False, tracked_length

    return next_point, direction, True, tracked_length


starting_angle = random.randint(0, 359)
starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
toward_circle_center = 180 + starting_angle
if toward_circle_center > 360: toward_circle_center -= 360
direction = toward_circle_center

# fill the screen in black
screen.fill(black)
pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)

while True:

    # reset screen if more than 30 lines
    if line_counter > 30:
        reinizialize()
        screen.fill(black)
        pygame.draw.circle(surface = screen, color = [100, 100, 100], center = screen_center, radius = circle_radius, width = circle_width)
        line_counter = 0


    update_inputs()


    line_counter += 1

    # completely random color
    brighter_color_index = random.randint(0, 2)
    linecolor = [random.randint(0, 250), random.randint(0, 250), random.randint(0, 250)]
    linecolor[brighter_color_index] = 250
    background_color = [ linecolor[0] // 2, linecolor[1] // 2, linecolor[2] // 2]

    # random linetype
    # linetype = random.randint(0, 2)


    # initialize internal parameters
    # starting_deflection = random.randint(0, 15)             # starting deflection
    left_right = 1 - random.randint(0, 1)*2        # starting direction (left/right)
    # the starting direction is from the starting point to the center of the circle
    start_line_length = 20
    tracked_length = start_line_length
    next_point = point_in_circle( starting_point, start_line_length, direction )
    pygame.draw.line(screen, linecolor, starting_point, next_point)
    pygame.draw.circle(surface = screen, color = linecolor, center = screen_center, radius = circle_radius, width = circle_width)
    if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)
    else: pygame.draw.circle(surface = screen, color = background_color, center = screen_center, radius = circle_radius + 2000, width = 2000)

    inside_circle = True
    start_straight = False
    while inside_circle:
        if inside_circle:            
            prev_tracked_length = tracked_length
            curve_type = curve_types[random.randint(0, 2)]
            end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
            tracked_length += length
            next_point = end_point
            direction = end_direction
            curve_type = curve_types[random.randint(0, 2)]
            left_right = -left_right
            end_point, end_direction, inside_circle, length = draw_random_curve(curve_type, next_point, direction, left_right, linecolor)
            tracked_length += length
            next_point = end_point
            direction = end_direction
            if tracked_length > 15*circle_radius:
                inside_circle = False
            if tracked_length == prev_tracked_length:
                inside_circle = False
                starting_angle = random.randint(0, 359)
                starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
                # start with a random point inside the circle
                toward_circle_center = 180 + starting_angle
                if toward_circle_center > 360: toward_circle_center -= 360
                direction = toward_circle_center

    # starting_point = next_point
    direction = direction - 180
    starting_point = point_in_circle( next_point, 2, direction )
    # starting_point = next_point

    
    if randomgen:
        starting_angle = random.randint(0, 359)
        starting_point = point_in_circle( screen_center, circle_radius, starting_angle )
        # start with a random point inside the circle
        toward_circle_center = 180 + starting_angle
        if toward_circle_center > 360: toward_circle_center -= 360
        direction = toward_circle_center

    
    
    screen2.blit(screen, (0,0))
    pygame.draw.circle(surface = screen, color = linecolor, center = screen_center, radius = circle_radius, width = circle_width)
    if strobo: pygame.draw.circle(surface = screen, color = [10, 10, 10], center = screen_center, radius = circle_radius + 2000, width = 2000)
    else: pygame.draw.circle(surface = screen, color = background_color, center = screen_center, radius = circle_radius + 2000, width = 2000)
    
    pygame.display.flip()
