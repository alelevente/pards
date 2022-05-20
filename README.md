# **Privacy-aware Real-time Data Sharing Among CAVs (PARDS)**

This repository contains the source codes to reproduce results published
by Levente Alekszejenkó and Tadeusz Dobrowiecki at the 11th IFAC Symposium on Intelligent Autonomous Vehicles (IAV 2022) entitled as `Privacy-aware Methods for Data Sharing between Autonomous Vehicles`.

## **The respository**

The repository contains the following files and directories:

- *cfg/*: configuration of measurement cases
- *data/*: input data for the simulation
- *results/*: simulation outputs are saved into this directory
- *src/*:
    - *simulation/*: source codes for running the simulation
    - *tools/*: miscellaneous functions supporting the simulation/visualization
    - *config_generator.ipynb*: helps to create new measurement case configurations
    - *measurement_tool.py*: this file contains functions called during simulation to measure the defined metrics
    - *measurement.py*: controls the simulation
    - *meeting_model.py*: determines which vehicles are meeting on the streets
    - *metrics.py*: definition of the metrics
    - *movement_tracker.py*: simple methods to track the movements of the vehicles
    - *network_creator.py*: to create new simulation input scenarios
    - *results_visualization.ipynb*: visualizes the results
    - *tell_decisions.py*: defintion of the data sharing methods mentioned in our article
    - *<measurement_case>.sh*: BASH scripts to run multiple simulations (some of them are run concurrently)

## **Usage**

As a prerequisite, [Eclipse SUMO](https://www.eclipse.org/sumo/) shall be installed. (PARDS needs partly similar inputs as Eclipse SUMO to perform simulations.)

The [environment.yml](environment.yml) contains the list of necessary packages to create a suitable conda environment to run the codes.

To run the codes, it is required to create a directory named `results` in the repository's root.

Please note, that it requires a significant amount of memory to visualize and analyse the results (e.g. 32 GiB on an Ubuntu 20.04 Server).

### Citation

Feel free to use our source codes to support your research/development, but please [cite](citation.bib) our work as:

`L. Alekszejenkó and T. Dobrowiecki, "Privacy-aware Methods for Data Sharing between Autonomous Vehicles", manuscript accepted for publication at the 11th IFAC Symposium on Intelligent Autonomous Vehicles, IAV 2022., 2022.`