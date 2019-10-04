import random
import numpy
import numpy as np
import matplotlib.pylab as plt
import itertools
from mpl_toolkits import mplot3d
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D

from lib.particle import Particle

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5



direction = [NE, E, SE, SW, W, NW]
info_plot=[[]]
info_plot_average=[[]]
info_plot_broud_cast_master_estimate=[[]]
filler_actual_count=[]
filler_actual_count.append(0)
calc_count=0
table_calcs= ""
aging_factor=0.1
initial_size=0
coord_map_calc=[[]]

def solution(world):
    global calc_count
    global table_calcs
    global initial_size
    global coord_map_calc
    global info_plot_average
    global  info_plot_broud_cast_master_estimate
    table_size_max = 16

    if world.get_actual_round()==1:
        initial_size=len(world.get_particle_list())

        #rows, cols = (int(world.get_world_x_size())*4, int(world.get_world_y_size())*4)
        #coord_map_calc = [[0] * cols] * rows

        #print(coord_map_calc)

        coord_map_calc=np.zeros((int(world.get_world_x_size())*4,int(world.get_world_y_size())*4 ), dtype=int)
        #print(test)

        #map for calculation count between junctions
        #for x in range(0, int(world.get_world_x_size())*4):
        #    coord_map_calc.append([0])

        #for x in range(1, int(world.get_world_x_size()) * 4):
        #    for y in range (0, int(world.get_world_y_size())*4-1):
        #        coord_map_calc[x].append(0)

        #coord_map_calc[int(world.get_world_x_size()*4-1)][int(world.get_world_y_size()*4-1)]=300

        for rnd_particle in world.get_particle_list():
            setattr(rnd_particle, "sum", 0)
            setattr(rnd_particle, "particle_count",0)
            #for average|min|max calc | local
            setattr(rnd_particle, "current_min", 0)
            setattr(rnd_particle, "current_max", 1)
            setattr(rnd_particle, "current_average", 1)
            setattr(rnd_particle, "min_rounds", 140)
            setattr(rnd_particle, "actual_round", 0)
            # for average|min|max calc | global
            setattr(rnd_particle, "min", 0)
            setattr(rnd_particle, "max", 1)
            setattr(rnd_particle, "average", 1)
            # version number
            setattr(rnd_particle, "version_number", 1)
            setattr(rnd_particle, "broud_cast_master_estimate", 1)


        #Graph
        master=random.choice(world.get_particle_list())
        master.sum=1
        master.version_number=2
        for i in range(len(world.get_particle_list())):
            info_plot.append([0])

        for particle in world.get_particle_list():
            info_plot_average.append([1])

        for particle in world.get_particle_list():
            info_plot_broud_cast_master_estimate.append([1])

    #Table
    if world.get_actual_round() == 1 and len(world.get_particle_list()) <= table_size_max:
        table_calcs = "|rounds  |"
        for i in range(0, len(world.get_particle_list())):
            table_calcs = table_calcs + "___p" + '{:_<4d}'.format(i) + "|"
        table_calcs = table_calcs + "\n" + "|round:_0|"
        helper_sum_list=[]
        for i in range(0, len(world.get_particle_list())):
            helper_sum_list.append(0)
        for particle in world.get_particle_list():
            print(particle.number)
            helper_sum_list[particle.number-1]=particle.sum
        for i in helper_sum_list:
            table_calcs=table_calcs+'{:_>8.4f}'.format(i)+"|"
        table_calcs+="\n|round:_1"


    #Table
    if world.get_actual_round() > 1 and len(world.get_particle_list()) <= table_size_max:
        table_calcs+="\n|round:" +'{:_>2d}'.format(world.get_actual_round()) + "|"



    ###################################################################################################################
    #Main Loop
    #
    #helper variable
    helper_particle_list = world.get_particle_list().copy()
    while(len(helper_particle_list)!=0):
        #choose a random particle
        rnd_particle=random.choice(helper_particle_list)
        current_sum = rnd_particle.sum
        #the random chosen particle searches for a neighbour
        neighbour_found_in_dir=search_any_neighbour(rnd_particle)
        rnd_particle_neighbour= rnd_particle.get_particle_in(neighbour_found_in_dir)
        #if the the random chosen particle has a sumvalue above 0
        #he will reach for the searched neighbour

        if(neighbour_found_in_dir!=-1):
            current_sum_neighbour=rnd_particle.get_particle_in(neighbour_found_in_dir).sum

            if abs((rnd_particle.current_max-rnd_particle.average))<np.ceil(rnd_particle.average*aging_factor/2) and \
                    abs(rnd_particle.current_min-rnd_particle.average)<np.ceil(rnd_particle.average*aging_factor/2) and \
                    abs((rnd_particle.current_max-rnd_particle.particle_count))<np.ceil(rnd_particle.particle_count*aging_factor/2) and\
                    abs((rnd_particle.current_min-rnd_particle.particle_count))<np.ceil(rnd_particle.particle_count*aging_factor/2) and \
                    rnd_particle.actual_round>=rnd_particle.min_rounds :
                reset_to_master(rnd_particle)

            print("version nr:", rnd_particle.version_number)

            if rnd_particle.version_number < rnd_particle_neighbour.version_number:
                reset_particle(rnd_particle,rnd_particle_neighbour)

            if rnd_particle.version_number > rnd_particle_neighbour.version_number:
                reset_particle(rnd_particle_neighbour,rnd_particle)

        if (neighbour_found_in_dir) != -1 and rnd_particle.version_number==rnd_particle_neighbour.version_number\
                and not (rnd_particle.sum==0 and rnd_particle.get_particle_in(neighbour_found_in_dir).sum==0):

            #aging information from last round
            consider_measurement(rnd_particle)
            consider_measurement(rnd_particle_neighbour)
            #adds the particle sum value with his neighbour's sum value and halves it eventually
            new_sum=transfer_sum(rnd_particle,rnd_particle_neighbour)
            #both particle get the new_sum
            rnd_particle.sum = new_sum
            rnd_particle_neighbour.sum= new_sum
            #particle_count
            rnd_particle.particle_count=calculate_particle_count(rnd_particle)
            rnd_particle_neighbour.particle_count=calculate_particle_count(rnd_particle_neighbour)
            #min|max|average exchange
            exchange_information(rnd_particle, rnd_particle_neighbour)
            #prints
            #print_information(rnd_particle,neighbour_found_in_dir, current_sum, current_sum_neighbour)
            #print("berechneten average:",rnd_particle.average)
            #print("current max", rnd_particle.current_max)
            #Table
            if(initial_size<=table_size_max):
                table_calcs+=next_line_table(world.get_particle_list())
                table_calcs += "  " + str(rnd_particle.number - 1) + "-->" + str(rnd_particle.get_particle_in(neighbour_found_in_dir).number - 1)

            #Amount of calculations between particles increased by 1
            calc_count+=1
            print("x: ", int(rnd_particle.coords[0]+world.get_world_x_size())*2)
            print("y: ", int(rnd_particle.coords[1]+world.get_world_y_size())*2)

            #print(coord_map_calc)

            coord_map_calc[int((rnd_particle.coords[0]+world.get_world_x_size())*2)-1][int((rnd_particle.coords[1]+world.get_world_y_size()*2)-1)]+=1
            coord_map_calc[int((rnd_particle_neighbour.coords[0]+world.get_world_x_size()*2)-1)][int((rnd_particle_neighbour.coords[1]+world.get_world_y_size()*2)-1)]+=1
            rnd_particle.actual_round += 1

        helper_particle_list.remove(rnd_particle)



    #Graph
    for particle in world.get_particle_list():
        info_plot[particle.number].append(particle.particle_count)

    for particle in world.get_particle_list():
        info_plot_average[particle.number].append(particle.average)

    for particle in world.get_particle_list():
        info_plot_broud_cast_master_estimate[particle.number].append(particle.broud_cast_master_estimate)

    #Color
    for particle in world.get_particle_list():
        farbe=set_color_g(particle)
        particle.set_color(farbe)

    print("ROUND:", world.get_actual_round())
    print("max round", world.get_max_round())



###########################################
#REMOVING PARTICLES
    #
    #if world.get_actual_round()==400:
    #     for i in range(0,50):
    #         rnd_particle=random.choice(world.get_particle_list())
    #         world.remove_particle(rnd_particle.get_id())
    #         print("removed and its now:", len(world.get_particle_list()))

    # if world.get_actual_round()==200:
    #     for i in range(0,10):
    #         rnd_particle=random.choice(world.get_particle_list())
    #         world.remove_particle(rnd_particle.get_id())
    #         print("removed and its now:", len(world.get_particle_list()))

##########################################


    filler_actual_count.append(len(world.get_particle_list()))

    if world.get_actual_round()== world.get_max_round():
        print("Terminated in round : ", world.get_actual_round())
        i=0
        for particle in world.get_particle_list():
            print("partikel_nr:",particle.number)
            print("schätzt partikelanzahl im system auf:",particle.particle_count)
            print("partikel_version_number",particle.version_number )


        ######################################################################################################
        ######################################################################################################
        #GRAPHS
        if len(world.get_particle_list()) <= table_size_max:
            for particle in world.get_particle_list():
                x = np.arange(1, world.get_actual_round() + 1, 1)
                #print(x)
                y = info_plot[particle.number]
                #print(y)
                #plt.figure(1)
                fig1,ax1 = plt.subplots()
                ax1.plot(x, y)
                ax1.plot(x, filler_actual_count)
                particle_number='Particle Number : '+ str(particle.number)
                ax1.set(xlabel='rounds',ylabel='Estimation of particles', title=particle_number)

        #average estimation per round
        average_plotter=[]
        for i in range(0, world.get_actual_round() + 1):
            sum_avg = 0
            for particle in world.get_particle_list():
                sum_avg+=info_plot[particle.number][i]
            average_plotter.append(sum_avg / len(world.get_particle_list()))
        #average_average_plotter
        average_average_plotter=[]
        for i in range(0,world.get_actual_round()+1):
            sum_avg_avg=0
            for particle in world.get_particle_list():
                sum_avg_avg+=info_plot_average[particle.number][i]
            average_average_plotter.append(sum_avg_avg/len(world.get_particle_list()))

        #average_broud_cast_master_estimate
        average_bcme_plotter=[]
        for i in range(0,world.get_actual_round()+1):
            sum_avg_m=0
            for particle in world.get_particle_list():
                sum_avg_m+=info_plot_broud_cast_master_estimate[particle.number][i]
            average_bcme_plotter.append(sum_avg_m/len(world.get_particle_list()))

        #min
        min_all_per_round=[]
        for i in range(0, world.get_actual_round() + 1):
            min_all_particle = []
            for particle in world.get_particle_list():
                min_all_particle.append(info_plot[particle.number][i])
            min_all_per_round.append(min(min_all_particle))
        #max
        max_all_per_round = []
        for i in range(0, world.get_actual_round() + 1):
            max_all_particle = []
            for particle in world.get_particle_list():
                #if(info_plot[particle.number][i]<=len(world.get_particle_list())*5):
                max_all_particle.append(info_plot[particle.number][i])
                #else:
                #    max_all_particle.append(len(world.get_particle_list()*5))
            max_all_per_round.append(max(max_all_particle))
        #standard deviation
        standard_deviation_per_round = []
        for i in range(0, world.get_actual_round() + 1):
            all_particle = 0
            for particle in world.get_particle_list():
                all_particle+=(info_plot[particle.number][i]-average_plotter[i])*(info_plot[particle.number][i]-average_plotter[i])
            s=(np.sqrt(all_particle) / len(world.get_particle_list()))/np.ceil(average_plotter[i])*100
            standard_deviation_per_round.append(s)

        #Graph 1
        x2 = np.arange(0, world.get_actual_round() + 1, 1)
        fig2,ax2=plt.subplots()
        ax2.plot(x2,average_plotter)
        ax2.plot(x2,filler_actual_count)
        ax2.plot(x2,min_all_per_round)
        ax2.plot(x2,max_all_per_round)

        if max(max_all_per_round)>50*len(world.get_particle_list()):
            ax2.set_yscale('log')
        ax2.set_ylim(ymin=1)
        ax2.set(xlabel='rounds', ylabel='Average', title='Rot:Max | Blau:Durchschnitt | Grün:Min | Orange:Echter Wert')

        #Graph 2
        y3=[]
        for i in x2:
            y3.append(5)

        fig3, ax3 = plt.subplots()
        ax3.plot(x2,standard_deviation_per_round, label='Prozentuale Standardabweichung')
        ax3.plot(x2, y3)
        ax3.set(xlabel='rounds', ylabel='standard deviation', title='Standard deviation')
        #ax3.set_yscale('log')
        ax3.legend(loc='upper left')

        #Graph 3
        print(coord_map_calc)
        print(len(coord_map_calc))
        for i in coord_map_calc[0]:
            #print(len(i))
            print("zeile :",coord_map_calc[i])


        #Graph4
        print(coord_map_calc)

        x4 = np.arange(0, world.get_world_x_size() * 4, 1)
        y4 = np.arange(0, world.get_world_y_size() * 4, 1)
        z4=[]
        for x in range(0,len(x4),2):
            for y in range(0,len(y4),2):
                z4.append(coord_map_calc[x][y])

        x4=np.arange(0, world.get_world_x_size()*4,2)
        y4=np.arange(0, world.get_world_y_size()*4,2)
        X, Y = np.meshgrid(x4, y4)
        fig4 = plt.figure()
        ax4 = fig4.add_subplot(111, projection='3d')

        X= X / 2 - world.get_world_x_size()
        Y= Y / 2 - world.get_world_y_size()

        print(X)
        print(Y)
        g1=0
        for i in X:
            if g1%2==0:
                X[g1]+=0.5
            g1+=1


        z4=np.array(z4)
        zz=np.copy(z4)
        z4=np.split(z4, world.get_world_y_size()*2)
        z4 = np.array(z4)

        avg_p=0
        c1=0
        for i in zz:
            avg_p+=zz[c1]
            c1+=1
        avg_p=avg_p/len(zz)

        print("ZZ:", zz)
        print(avg_p)

        standard_dev_p=0
        c1=0
        for i in zz:
            standard_dev_p+=(avg_p-zz[c1])*(avg_p-zz[c1])
            c1+=1

        standard_dev_p=np.sqrt(standard_dev_p/avg_p)
        print("zz standarddev: ", standard_dev_p)

        standard_dev_p_relativ= (standard_dev_p/avg_p)*100



        im=ax4.plot_surface(X, Y, z4 , cmap='jet')
        ax4.set_xlabel('X coord')
        ax4.set_ylabel('Y coord')
        ax4.set_zlabel('Austausche')
        fig4.colorbar(im)


        #Graph 5

        titel="Standardabweichung in Prozent: "+str(standard_dev_p_relativ)+"%"
        fig5, ax5 = plt.subplots()
        a5=ax5.scatter(X, Y, c=z4, cmap='jet')
        ax5.set(title=titel)
        fig5.colorbar(a5)

        #Graph 6
        x6 = np.arange(0, world.get_actual_round() + 1, 1)
        fig6, ax6 = plt.subplots()
        l1=ax6.plot(x2, average_plotter, label='Average of current estimations')
        l2=ax6.plot(x2, filler_actual_count, label='Actual particle count in the system')
        l3=ax6.plot(x2, average_average_plotter, label='Average of average estimations')
        ax6.plot(x2, average_bcme_plotter, label='broadcasted estimates')
        ax6.set(xlabel='rounds', ylabel='Average', title='Estimation comparisons')
        ax6.legend(loc='upper left')
        if max(average_plotter)>50*len(world.get_particle_list()):
            ax6.set_yscale('log')
        ax6.set_ylim(ymin=1)



        #Graphs
        ####################################################################################################

        ####################################################################################################
        #Print Information
        if world.get_actual_round() > 1 and len(world.get_particle_list()) <= table_size_max:
            table_calcs+=next_line_table(world.get_particle_list())
            print(table_calcs)
        print("Calculation count between particles", calc_count)
        print("Calculations per node", calc_count / (world.get_world_y_size() * world.get_world_x_size()))
        print("Average estimation:", average_plotter[len(average_plotter)-1])
        # Abweichung : Tatsächlicher Wert / Durchschnittswert | Min | Max ( all particle ) | Standardabweichung
        # absolut/relativ
        absolute_deviation=  average_plotter[len(average_plotter)-1]-len(world.get_particle_list())
        relative_deviation= (average_plotter[len(average_plotter)-1] / len(world.get_particle_list()) - 1) * 100
        max_all_time= max(max_all_per_round)
        min_all_time= min(min_all_per_round)
        max_last_round= max_all_per_round[len(max_all_per_round)-1]
        min_last_round= min_all_per_round[len(min_all_per_round)-1]

        standard_deviation_last_round = standard_deviation_per_round[len(standard_deviation_per_round)-1]
        relative_standard_deviation = (standard_deviation_last_round/average_plotter[len(average_plotter)-1])*100

        difference_max_average_last_round=max_last_round-average_plotter[len(average_plotter)-1]
        difference_min_average_last_round=min_last_round-average_plotter[len(average_plotter)-1]

        print("Deviation : Average estimation - Particles (absolute): ",absolute_deviation, " (relativ:)",relative_deviation,"%")
        print("(all rounds): Max: ",max_all_time, " Min: ", min_all_time)
        print("(last round): Max: ",max_last_round, "Min: ", min_last_round)
        print("difference Max-average: ", difference_max_average_last_round, " Min-average: ", difference_min_average_last_round)
        print("Standard deviation (last round): ", standard_deviation_last_round, "(relativ:)",relative_standard_deviation ,"%"  )
        print(standard_deviation_per_round)
        #for rnd_particle in world.get_particle_list():
        #    print("partikel number:", rnd_particle.number)
        #    print("curr average:", rnd_particle.current_average)
        #    print("curr min:", rnd_particle.current_min)
        #    print("curr max:", rnd_particle.current_average)
        #    print("curr count:", rnd_particle.particle_count)
        plt.show()
        world.set_end()

#######################################################################################################################
#Moving
    #every particle moves after exchanging information
    if world.get_actual_round() > 0:
        for particle in world.get_particle_list():
            free_space_in_dir=search_personal_space(particle)
            if free_space_in_dir != -1:
                particle.move_to(free_space_in_dir)

#######################################################################################################################
# Methods
def reset_to_master(particle):
    particle.sum=1
    particle.broud_cast_master_estimate=particle.particle_count
    particle.particle_count = 1
    particle.current_min = 1
    particle.current_max = 1
    particle.current_average = 1
    particle.version_number=int(particle.version_number+random.randint(1,round(particle.average)))
    particle.actual_round=0


def reset_particle(rnd_particle, rnd_particle_neighbour):
    rnd_particle.sum = 0
    rnd_particle.particle_count= 0
    rnd_particle.current_min = 0
    rnd_particle.current_max = 1
    rnd_particle.current_average = 1
    rnd_particle.version_number= rnd_particle_neighbour.version_number
    if rnd_particle.actual_round>=rnd_particle.min_rounds/2:
        rnd_particle.broud_cast_master_estimate=rnd_particle_neighbour.broud_cast_master_estimate
    rnd_particle.min_rounds=rnd_particle_neighbour.min_rounds
    rnd_particle.actual_round = 0

def exchange_information(rnd_particle,rnd_particle_neighbour):
    #min
    rnd_particle.current_min = min(rnd_particle.particle_count, rnd_particle_neighbour.particle_count)
    rnd_particle_neighbour.current_min = min(rnd_particle.particle_count, rnd_particle_neighbour.particle_count)
    # max
    rnd_particle.current_max = max(rnd_particle.particle_count, rnd_particle_neighbour.particle_count)
    rnd_particle_neighbour.current_max = max(rnd_particle.particle_count, rnd_particle_neighbour.particle_count)
    # average
    rnd_particle.current_average = (rnd_particle.particle_count + rnd_particle_neighbour.particle_count) / 2
    rnd_particle_neighbour.current_average = (rnd_particle.particle_count + rnd_particle_neighbour.particle_count) / 2




#aging function
def consider_measurement(particle):
    particle.min=(1-aging_factor)*particle.min+aging_factor*particle.current_min
    particle.max=(1-aging_factor)*particle.max+aging_factor*particle.current_max
    particle.average=(1-aging_factor)*particle.average+aging_factor*particle.current_average


def print_information(rnd_particle, neighbour_found_in_dir, current_sum,current_sum_neighbour ):
    print("current_sum:", current_sum)
    print("other particle's current_sum", current_sum_neighbour)
    print("after calc:", rnd_particle.sum)
    print("N:after calc:", rnd_particle.get_particle_in(neighbour_found_in_dir).sum)
    print("particle aprox:", rnd_particle.particle_count)
    print("N:particle aprox:", rnd_particle.get_particle_in(neighbour_found_in_dir).particle_count)
    print("difference: old/new sum:", abs(current_sum - rnd_particle.sum))


def next_line_table(p_list):
    helper_sum_list=[]
    global table_calcs
    next_line="\n|calc:" + '{:_>3d}'.format(calc_count) + "|"
    for i in range(0, len(p_list)):
        helper_sum_list.append(0)
    for particle in p_list:
        helper_sum_list[particle.number - 1] = particle.sum
    for i in helper_sum_list:
        next_line+= '{:_>8.4f}'.format(i) + "|"
    return next_line


def search_personal_space(particle):
    dir = [0, 1, 2, 3, 4, 5]
    while len(dir) != 0:
        rnd_dir = random.choice(dir)
        if particle.particle_in(rnd_dir):
            dir.remove(rnd_dir)
        else:
            return rnd_dir
    return -1


def search_any_neighbour(particle: Particle) -> int:
    #searches for any neighbour to transfer sum afterwards
    dir = [0,1,2,3,4,5]
    while len(dir)!=0:
        rnd_dir=random.choice(dir)
        if particle.particle_in(rnd_dir):
            return rnd_dir
        else:
            dir.remove(rnd_dir)
    return -1


def transfer_sum(particle1,particle2):
    return (particle1.sum+particle2.sum)/(2)


def calculate_particle_count(particle):
    #berechnet den Kehrwert der Summe um die geschätzte Anzahl der Partikel im System zu berechnen
    return round(1/particle.sum)

def set_color_g(particle):
    #colour =1 : <10
    #colour =2 : <20
    #colour =3 : <50
    #colour =4 : <100
    #colour =5 : <200
    #colour =6 : >=200
    # black = 1
    # gray = 2
    # red = 3
    # green = 4
    # blue = 5
    # yellow = 6
    # orange = 7
    # cyan = 8
    # violett = 9
    if particle.particle_count>=200:
        return 6
    elif particle.particle_count>=100:
        return 5
    elif particle.particle_count>=50:
        return 4
    elif particle.particle_count>=20:
        return 3
    elif particle.particle_count>=10:
        return 2
    else:
        return 1

