"""
A world is created that has particles formated in a ring structure that is up to 5 hops big
"""


def scenario(world):
    world.add_particle(0, 0, color=3)
    # 1st ring
    world.add_particle(1.000000, 0.000000, color=1)
    world.add_particle(-1.000000, 0.000000, color=1)
    world.add_particle(0.500000, 1.000000, color=1)
    world.add_particle(0.500000, -1.000000, color=1)
    world.add_particle(-0.500000, 1.000000, color=1)
    world.add_particle(-0.500000, -1.000000, color=1)

    # 2nd ring
    world.add_tile(2.000000, 0.000000, color=2)
    world.add_tile(-2.000000, 0.000000, color=2)
    world.add_tile(1.500000, 1.000000, color=2)
    world.add_tile(1.500000, -1.000000, color=2)
    world.add_tile(-1.500000, 1.000000, color=2)
    world.add_tile(-1.500000, -1.000000, color=2)
    world.add_tile(1.000000, 2.000000, color=2)
    world.add_tile(1.000000, -2.000000, color=2)
    world.add_tile(0.000000, 2.000000, color=2)
    world.add_tile(0.000000, -2.000000, color=2)
    world.add_tile(-1.000000, 2.000000, color=2)
    world.add_tile(-1.000000, -2.000000, color=2)

    # 3rd ring
    world.add_marker(3.000000, 0.000000, color=3)
    world.add_marker(-3.000000, 0.000000, color=3)
    world.add_marker(2.500000, 1.000000, color=3)
    world.add_marker(2.500000, -1.000000, color=3)
    world.add_marker(-2.500000, 1.000000, color=3)
    world.add_marker(-2.500000, -1.000000, color=3)
    world.add_marker(2.000000, 2.000000, color=3)
    world.add_marker(2.000000, -2.000000, color=3)
    world.add_marker(-2.000000, 2.000000, color=3)
    world.add_marker(-2.000000, -2.000000, color=3)
    world.add_marker(1.500000, 3.000000, color=3)
    world.add_marker(1.500000, -3.000000, color=3)
    world.add_marker(0.500000, 3.000000, color=3)
    world.add_marker(0.500000, -3.000000, color=3)
    world.add_marker(-0.500000, 3.000000, color=3)
    world.add_marker(-0.500000, -3.000000, color=3)
    world.add_marker(-1.500000, 3.000000, color=3)
    world.add_marker(-1.500000, -3.000000, color=3)


