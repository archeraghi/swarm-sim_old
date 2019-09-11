import lib.oppnet.routing
from lib.oppnet import opp_solution
from lib.oppnet.comms import generate_random_messages
from lib.oppnet.mobility_model import MobilityModel


def solution(sim):
    particles = sim.get_particle_list()

    if sim.get_actual_round() == 1:
        # initialize the particle mobility models
        for particle in particles[:4]:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], sim.mobility_model_mode)
            m_model.set(particle)
            r_params = lib.oppnet.routing.RoutingParameters(algorithm=sim.routing_algorithm,
                                                            scan_radius=2,
                                                            delivery_delay=sim.delivery_delay)
            r_params.set(particle)
        # initially generate 5 message per particle on the edge
        messages = generate_random_messages(particles[:4], amount=5, sim=sim)

        for particle in particles[4:]:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], sim.mobility_model_mode)
            m_model.set(particle)
            r_params = lib.oppnet.routing.RoutingParameters(algorithm=sim.routing_algorithm,
                                                            scan_radius=3,
                                                            delivery_delay=sim.delivery_delay)
            r_params.set(particle)

    else:
        for particle in particles:
            m_model = MobilityModel.get(particle)
            particle.move_to_in_bounds(m_model.next_direction())

        lib.oppnet.routing.next_step(particles, sim.get_actual_round())

    opp_solution.process_event_queue(sim)
