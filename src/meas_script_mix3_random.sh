#!/bin/bash

echo "asymmetric low"
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix123/ -n 1 2 3 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix1/ -n 1 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix2/ -n 2 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix3/ -n 3 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix12/ -n 1 2 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix13/ -n 1 3 &
python3 measurement.py ../cfg/asymmetric_low_random.json ../results/random/low/asymmetric/mix23/ -n 2 3 

echo "symmetric low"
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix1/ -n 1 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix2/ -n 2 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix3/ -n 3 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix12/ -n 1 2 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix13/ -n 1 3 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix23/ -n 2 3 &
python3 measurement.py ../cfg/symmetric_low_random.json ../results/random/low/symmetric/mix123/ -n 1 2 3 



echo "asymmetric medium"
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix1/ -n 1 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix2/ -n 2 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix3/ -n 3 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix12/ -n 1 2 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix13/ -n 1 3 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix23/ -n 2 3 &
python3 measurement.py ../cfg/asymmetric_medium_random.json ../results/random/medium/asymmetric/mix123/ -n 1 2 3 

echo "symmetric medium"
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix1/ -n 1 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix2/ -n 2 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix3/ -n 3 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix12/ -n 1 2 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix13/ -n 1 3 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix23/ -n 2 3 &
python3 measurement.py ../cfg/symmetric_medium_random.json ../results/random/medium/symmetric/mix123/ -n 1 2 3 



echo "asymmetric high"
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix1/ -n 1 &
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix2/ -n 2 
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix3/ -n 3 &
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix12/ -n 1 2
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix13/ -n 1 3 &
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix23/ -n 2 3
python3 measurement.py ../cfg/asymmetric_high_random.json ../results/random/high/asymmetric/mix123/ -n 1 2 3 &

echo "symmetric high"
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix1/ -n 1
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix2/ -n 2 &
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix3/ -n 3
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix12/ -n 1 2 &
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix13/ -n 1 3
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix23/ -n 2 3 &
python3 measurement.py ../cfg/symmetric_high_random.json ../results/random/high/symmetric/mix123/ -n 1 2 3
