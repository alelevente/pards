'''This file contains utility functions including:
- visualization'''

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
        c_norm = matplotlib.colors.LogNorm(vmin=min(probabilities)*0.85+0.0001, vmax=max(probabilities)*1.15)
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
    def __init__(self, base_matrix):
        self.base_matrix = np.array(base_matrix)
        
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