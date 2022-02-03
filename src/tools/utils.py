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
                colors[index_to_edge_map[i]] = scalar_map.to_rgba(p)
    
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
        for i in range(1, max_n):
            self.powers[i] = self.powers[i-1] @ base_matrix
        
    def __call__(self, n):
        if not(n in self.powers):
            self.powers[n] = np.linalg.matrix_power(self.base_matrix, n)
        return self.powers[n]


##########################################
############ OTHER HELPERS ###############
def read_MC(network_path: str, turning_path: str, default_turning_rates: list):
    '''
        Reads a SUMO network and the turning description file. Then converts them into a MC.
        Parameters:
            network_path: path to the SUMO road network file
            turning_path: path to the turning definition file
        Return:
            P: transition matrix of the MC
            edge_to_index_map: network edges -> indices of P
            index_to_edge_map: indices of P -> network edges
    '''
    
    net = sumolib.net.readNet(network_path)
    turning_desc = pd.read_xml(turning_path, xpath="./interval/*")
    return mc.create_transition_matrix(net, default_turning_rates, turning_desc)

def sample_route_lengths(a, num_samples):
    p_m = 1/a
    ds = np.arange(1, 2*a+1)
    return np.array([2*p_m/a*d if d<=a/2 else -2*p_m/(3*a)*d+4/3*p_m for d in ds])

def sample_route_lengths_uniform(a, num_samples):
    p_m = 1/a
    ds = np.arange(1, 2*a+1)
    return np.array([1/(a**2)*d if d<=a else -1/(a**2)*d+2/a for d in ds])


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
    records = measurement_tool.distance_records
    #data = np.array([records.method, records.ids, records.times, records.distances, records.distance_diffs]).T
    #minimizing memory usage:
    distance_df = pd.DataFrame()
    distance_df.insert(0, "id", records.ids)
    distance_df.insert(1, "time", records.times)
    distance_df.insert(2, "method", records.method)
    distance_df.insert(3, "Alter correctness", records.distances)
    distance_df.insert(4, "Distance difference", records.distance_diffs)
    return distance_df

def save_results(measurement_tool, path_to_save):
    start = time.time()
    iongs = create_iongs_dataframe(measurement_tool)
    print("IONG collected in %f seconds"%(time.time()-start))
    
    start = time.time()
    distances = create_distance_dataframe(measurement_tool)
    print("Distances collected in %f seconds"%(time.time()-start))
    iongs.to_csv(path_to_save+"iong.csv", index=False)
    distances.to_csv(path_to_save+"distances.csv", index=False)
    return iongs, distances