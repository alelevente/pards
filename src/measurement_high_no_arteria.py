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
    P, edge_to_index_map, index_to_edge_map = tools.utils.read_MC("../data/large_grid2_noart.net.xml",
                                                       "../data/turnings2.xml",
                                                       [.3, .5, .2])
    net = sumolib.net.readNet("../data/large_grid2_noart.net.xml")
    P_ = P
    π = tools.mc.calculate_stationary_distribution(P_)#[:-1]/np.sum(tools.mc.calculate_stationary_distribution(P_)[:-1])
    P_b = tools.mc.calculate_time_reversed_mc(P_, π)
    matrix_power = tools.utils.MatrixPower(P_b)
    initial_state_model = np.ones(len(P))/len(P)
    
    #Feeding model:
    feeding_model = np.ones(1000)*16.0
    path_length_model = tools.utils.sample_route_lengths_uniform(20, np.sum(feeding_model))
    
    measurement_tool = measurement_tool.MeasCallback(net, P_, P_b, edge_to_index_map, index_to_edge_map,
                                initial_state_model, matrix_power, path_length_model)
    sim = simulator.Simulator(P_, feeding_model, initial_state_model, path_length_model)

    start_time = time.time()
    run_steps = sim.simulate(callback_function=measurement_tool)
    stop_time = time.time()

    print("Simulator finished in {} steps, computed in {} seconds".format(run_steps, stop_time-start_time))
    
    tools.utils.save_results(measurement_tool, "../results/no_arteria/high_uniform/")