import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import tools
import simulation.simulator as simulator
import measurement_tool

import metrics

import time
import sumolib


def sample_route_lengths(a, num_samples):
    p_m = 1/a
    ds = np.arange(1, 2*a+1)
    return np.array([2*p_m/a*d if d<=a/2 else -2*p_m/(3*a)*d+4/3*p_m for d in ds])


def create_iongs_dataframe(measurement_tool):
    iongs_uniform = []
    iongs_minprob = []
    iongs_last1 = []
    iongs_last2 = []
    iongs_last3 = []
    iongs_mix = []
    ids = []

    for _id in measurement_tool.movement_tracker.movements:
        ids.append(_id)
        #if a vehicle received information, it gathered additional information:
        if _id in measurement_tool.received_information_uniform:
            iongs_uniform.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_uniform[_id]))
            iongs_minprob.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_minprob[_id]))
            iongs_last1.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_last1[_id]))
            iongs_last2.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_last2[_id]))
            iongs_last3.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_last3[_id]))
            iongs_mix.append(metrics.compute_iong(measurement_tool.movement_tracker.movements[_id],
                                         measurement_tool.received_information_mix[_id]))

        else:
            #otherwise, it did not:
            iongs_uniform.append(-1)
            iongs_minprob.append(-1)
            iongs_last1.append(-1)
            iongs_last2.append(-1)
            iongs_last3.append(-1)
            iongs_mix.append(-1)
    
    answer = pd.DataFrame(np.array([ids, iongs_uniform, iongs_minprob, iongs_last1, iongs_last2, iongs_last3, iongs_mix]).T,
                         columns = ["id", "uniform", "minprob", "last1", "last2", "last3", "mix"])
    return answer

def create_distance_dataframe(measurement_tool):
    legends = ["uniform", "minprob", "last1", "last2", "last3", "mix"]
    
    distances_per_telling = [[] for i in range(len(legends))]
    ids = [[] for i in range(len(legends))]
    
    for _id in measurement_tool.distances:
        for t in measurement_tool.distances[_id]:
            for i,dist in enumerate(measurement_tool.distances[_id][t]):
                distances_per_telling[i] = distances_per_telling[i] + dist
                ids[i] = ids[i] + [_id]*len(dist)
                
    data = []
    for i, l in enumerate(legends):
        for j,d in enumerate(distances_per_telling[i]):
            data.append([l, ids[i][j], d])
    return pd.DataFrame(data, columns=["method", "id", "Alter correctness\ndistance [m]"])

def save_results(measurement_tool, path_to_save):
    iongs = create_iongs_dataframe(measurement_tool)
    distances = create_distance_dataframe(measurement_tool)
    iongs.to_csv(path_to_save+"iong.csv", index=False)
    distances.to_csv(path_to_save+"distances.csv", index=False)
    return iongs, distances



if __name__ == "__main__":
    #Initialization:
    P, edge_to_index_map, index_to_edge_map = tools.utils.read_MC("../data/large_grid2.net.xml",
                                                       "../data/turnings.xml",
                                                       [.15, .8, .05])
    net = sumolib.net.readNet("../data/large_grid2.net.xml")
    P_ = tools.mc.add_st_node(P, [0.0, 0.0]) #prevents cars that have left the network to return
    π = tools.mc.calculate_stationary_distribution(P_)#[:-1]/np.sum(tools.mc.calculate_stationary_distribution(P_)[:-1])
    P_b = tools.mc.calculate_time_reversed_mc(P_, π)
    matrix_power = tools.utils.MatrixPower(P_b)
    initial_state_model = π
    
    #Feeding model:
    feeding_model = np.zeros(30)
    for i in range(len(feeding_model)//2):
        feeding_model[i*2] = 1.0
    path_length_model = sample_route_lengths(20, np.sum(feeding_model))
    
    measurement_tool = measurement_tool.MeasCallback(net, P_, P_b, edge_to_index_map, index_to_edge_map,
                                π, matrix_power, path_length_model)
    sim = simulator.Simulator(P_, feeding_model, initial_state_model, path_length_model)

    start_time = time.time()
    run_steps = sim.simulate(callback_function=measurement_tool)
    stop_time = time.time()

    print("Simulator finished in {} steps, computed in {} seconds".format(run_steps, stop_time-start_time))
    print(measurement_tool.times)
    
    save_results(measurement_tool, "../results/profiler/")