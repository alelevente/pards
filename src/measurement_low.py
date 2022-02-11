import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import tools
import simulation.simulator as simulator
import measurement_tool

import metrics

import time
import sumolib


if __name__ == "__main__":
    #Initialization:
    P, edge_to_index_map, index_to_edge_map = tools.utils.read_MC("../data/large_grid2.net.xml",
                                                       "../data/turnings.xml",
                                                       [.15, .8, .05])
    net = sumolib.net.readNet("../data/large_grid2.net.xml")
    P_ = tools.mc.add_st_node(P) #prevents cars that have left the network to return
    π = tools.mc.calculate_stationary_distribution(P_)#[:-1]/np.sum(tools.mc.calculate_stationary_distribution(P_)[:-1])
    P_b = tools.mc.calculate_time_reversed_mc(P_, π)
    matrix_power = tools.utils.MatrixPower(P_b)
    initial_state_model = np.ones(len(P))/len(P)
    term_edges = set(tools.mc.list_terminating_edges(P))
    
    #Feeding model:
    feeding_model = np.zeros(1000)
    for i in range(len(feeding_model)//2):
        feeding_model[i*2] = 1.0
    path_length_model = tools.utils.sample_route_lengths_uniform(20, np.sum(feeding_model))
    
    measurement_tool = measurement_tool.MeasCallback(net, P_, P_b, edge_to_index_map, index_to_edge_map,
                                initial_state_model, matrix_power, path_length_model)
    sim = simulator.Simulator(P_, feeding_model, initial_state_model, path_length_model,
                        term_edges)

    start_time = time.time()
    run_steps = sim.simulate(callback_function=measurement_tool)
    stop_time = time.time()

    print("Simulator finished in {} steps, computed in {} seconds".format(run_steps, stop_time-start_time))
    
    tools.utils.save_results(measurement_tool, "../results/arteria/low_uniform/")