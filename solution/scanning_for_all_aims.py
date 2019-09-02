"""
This solution just scans for particles that are within 5 hops range and prints them out.
"""

#Standard Lib that has to be in each solution
from solution.std_lib import *

def solution(world):

    all_matters_list=[]
    if world.get_actual_round() == 1:
        all_matters_list=world.get_particle_map_coords()[(0,0)].scan_for_matters_within(hop=5)
        for list in all_matters_list:
            if list.type=='particle':
                print ("particle at", list.coords)
            elif list.type=='tile':
                print("tile", list.coords)
            elif list.type=='marker':
                print("marker", list.coords)
    if world.get_actual_round() == 2:
        all_matters_list = world.get_particle_map_coords()[(0, 0)].scan_for_particles_within(hop=5)
        for list in all_matters_list:
            print ("particle at", list.coords)
        all_matters_list = world.get_particle_map_coords()[(0, 0)].scan_for_tiles_within(hop=5)
        for list in all_matters_list:
            print("tile", list.coords)
        all_matters_list = world.get_particle_map_coords()[(0, 0)].scan_for_markers_within(hop=5)
        for list in all_matters_list:
            print("marker", list.coords)
