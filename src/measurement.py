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
    
    args = parser.parse_args()
    config = {}
    with open(args.config_file) as f:
        config = json.load(f)
        
    