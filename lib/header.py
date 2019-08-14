from enum import Enum


class Colors(Enum):
    black = 1
    gray = 2
    red = 3
    green = 4
    blue = 5
    yellow = 6
    orange = 7
    cyan = 8
    violett = 9


black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9


color_map = {
    black: [0.0, 0.0, 0.0],
    gray: [0.3, 0.3, 0.3],
    red: [0.8, 0.0, 0.0],
    green: [0.0, 0.8, 0.0],
    blue: [0.0, 0.0, 0.8],
    yellow: [0.8, 0.8, 0.0],
    orange: [0.8, 0.3, 0.0],
    cyan: [0.0, 0.8, 0.8],
    violett: [0.8, 0.2, 0.6]
}


NE=0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

x_offset = [0.5, 1,  0.5,   -0.5,   -1, -0.5 ]
y_offset = [ 1, 0, -1,   -1,    0,  1]


def dir_to_str(dir):
    """
    :param dir: the direction that should get converted to a string
    :return: the string of the direction
    """
    if dir == 0:
        return "NE"
    elif dir == 1:
        return "E"
    elif dir == 2:
        return "SE"
    elif dir == 3:
        return "SW"
    elif dir == 4:
        return "W"
    elif dir == 5:
        return "NW"
    else:
        return "Error"


def get_the_invert(dir):
    return (dir + 3) % 6


def dir_in_range(dir):
    return dir % 6
