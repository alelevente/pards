import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import tools
import simulation.simulator as simulator
import measurement_tool

import metrics

import time
import sumolib

import argparse
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="configuration json file")
    parser.add_argument("result_path", type=str, help="path where the results will be saved to")
    parser.add_argument('-n','--mix_n', nargs='+', help='<Required> n values for mix method', required=True,
                       )#type=lambda s: [int(item) for item in s.split(',')])
    
    args = parser.parse_args()
    config = {}
    with open(args.config_file) as f:
        config = json.load(f)
    mix_n = [int(x) for x in args.mix_n]
    print(mix_n)
        
    P, edge_to_index_map, index_to_edge_map = tools.mc.read_MC(
        config["sumo_grid"],
        config["specific_turning_definition"],
        config["default_turning_definition"])
    net = sumolib.net.readNet(config["sumo_grid"])
    P_ = P
    π = tools.mc.calculate_stationary_distribution(P_)
    P_b = tools.mc.calculate_time_reversed_mc(P_, π)
    matrix_power = tools.utils.MatrixPower(P_b)
    measurement_tool = measurement_tool.MeasCallback(net, P_, P_b, edge_to_index_map, index_to_edge_map,
                                config["feeding_model"]["origin_model"],
                                matrix_power,
                                config["feeding_model"]["path_length_model"],
                                mix_n)
    sim = simulator.Simulator(P_,
                              config["feeding_model"]["feed"],
                              config["feeding_model"]["origin_model"], 
                              config["feeding_model"]["path_length_model"])

    start_time = time.time()
    run_steps = sim.simulate(callback_function=measurement_tool)
    stop_time = time.time()

    print("Simulator finished in {} steps, computed in {} seconds".format(run_steps, stop_time-start_time))
    
    tools.utils.save_results(measurement_tool, args.result_path)
    
    
    