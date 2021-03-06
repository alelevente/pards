'''This file contains utility functions including:
- visualization'''

import time
import json
import math

import numpy as np
import pandas as pd

import matplotlib.colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt

import sumolib
from sumolib.visualization import helpers
import tools.mc as mc

import io
import imageio

import os
import sys
sys.path.append("../")
import metrics

import torch

class Option:
    #default options required by sumolib.visualization
    defaultWidth = 1.5
    defaultColor = (0.0, 0.0, 0.0, 0.0)


#################################################
############  PLOTTING FUNCTIONS ################
def plot_network_probs(net, probabilities, index_to_edge_map, cmap="YlGn",
                      title="", special_edges=None):

    '''
        Plots a road network with edges colored according to a probabilistic distribution.
        Parameters:
            net: a sumolib road network
            probabilities: a dictionary that maps edge indices to probabilities
                If an edge is not in this map, it will get a default (light gray) color.
            index_to_edge_map: a dictionary that maps edge indices to SUMO edge IDs
            cmap: the colormap to be used on the plot
            title: title of the produced plot
            special_edges: edges to be plotted with special color, given in a similar structure
                as probabilities parameter

        Returns:
            a figure and axis object
    '''
        
    scalar_map = None
    colors = {}
    options = Option()
    if probabilities is None:
        for e in index_to_edge_map.values():
            colors[e] = (0.125, 0.125, 0.125, .25)
    else:
        c_norm = matplotlib.colors.LogNorm(vmin=min(probabilities)*0.85, vmax=max(probabilities)*1.15)
        scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=cmap)
        for i,p in enumerate(probabilities):
            if (p == 0.0) and (i in index_to_edge_map):
                colors[index_to_edge_map[i]] = (0.125, 0.125, .125, .125)
            elif i in index_to_edge_map:
                colors[index_to_edge_map[i]] = scalar_map.to_rgba(min(1,max(0,p)))
    
    if not(special_edges is None):
        for ind in special_edges:
            colors[index_to_edge_map[ind]] = (1., 0, 0, 1.)
    
    fig, ax = plt.subplots(figsize=(22, 20))
    helpers.plotNet(net, colors, [], options)
    plt.title(title)
    plt.xlabel("position [m]")
    plt.ylabel("position [m]")
    ax.set_facecolor("lightgray")
    if not(scalar_map is None):
        plt.colorbar(scalar_map)

    return fig, ax

def create_gif(plots, gif_name, duration=1.0):
    '''
        Creates a gif out of a list of plots.
        Parameters:
            plots: a list of figures
            gif_name: the filename of the outputted gif
            duration: duration while a single image is displayed
    '''

    os.mkdir("./.gif_creator")
    images = []
    for i, plot in enumerate(plots):
        filename = "./.gif_creator/%d.png"%i
        plot.savefig(filename)
        images.append(imageio.imread(filename))
        os.remove(filename)
    
    os.rmdir("./.gif_creator")
    imageio.mimsave(gif_name, images, duration)


##########################################
###### COMPUTATIONAL FUNCTIONS ###########
class MatrixPower:
    '''
        Provides fast calculation of matrix power by storing
        previous results in the memory.
    '''
    powers = {}
    def __init__(self, base_matrix, max_n=40):
        self.base_matrix = np.array(base_matrix)
        self.powers[0] = base_matrix
        #for faster calculation on GPU:
        if torch.cuda.is_available():
            base = torch.from_numpy(base_matrix).to("cuda")
            y = torch.from_numpy(base_matrix).to("cuda")
            with torch.no_grad():
                for i in range(1, max_n):
                    y = y @ base
                    self.powers[i] = y.to("cpu").numpy()
        else:
            for i in range(1, max_n):
                self.powers[i] = self.powers[i-1] @ base_matrix
        
    def __call__(self, n):
        if not(n in self.powers):
            self.powers[n] = np.linalg.matrix_power(self.base_matrix, n)
        return self.powers[n]


##########################################
############ OTHER HELPERS ###############
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

def create_distance_data(measurement_tool, filename):
    #records = measurement_tool.distance_records
    #data = np.array([records.method, records.ids, records.times, records.distances, records.distance_diffs]).T
    #minimizing memory usage:
    #distances = {
    #    "ids": records.ids,
    #    "times": records.times,
    #    "method": records.method,
    #    "alter_correctness": records.distances,
    #    "distance_difference": records.distance_diffs
    #}
    '''distance_df = pd.DataFrame()
    distance_df.insert(0, "id", records.ids)
    distance_df.insert(1, "time", records.times)
    distance_df.insert(2, "method", records.method)
    distance_df.insert(3, "Alter correctness", records.distances)
    distance_df.insert(4, "Distance difference", records.distance_diffs)'''
    with open(filename, "w") as f:
        f.write("id,time,method,Alter correctness,Distance difference\n")
        for i in range(len(measurement_tool.distance_records.ids)):
            f.write("%d,%d,%s,%d,%d\n"%(
                int(measurement_tool.distance_records.ids[i]),
                measurement_tool.distance_records.times[i],
                measurement_tool.distance_records.method[i],
                measurement_tool.distance_records.distances[i],
                measurement_tool.distance_records.distance_diffs[i]))
    return None

def save_results(measurement_tool, path_to_save):
    start = time.time()
    iongs = create_iongs_dataframe(measurement_tool)
    print("IONG collected in %f seconds"%(time.time()-start))
    
    start = time.time()
    distances = create_distance_data(measurement_tool, path_to_save+"distances.csv")
    print("Distances collected in %f seconds"%(time.time()-start))
    iongs.to_csv(path_to_save+"iong.csv", index=False)
    #with open(path_to_save+"distances.json", "w") as f:
    #    json.dump(distances, f)
    #distances.to_csv(path_to_save+"distances.csv", index=False)
    return iongs, distances