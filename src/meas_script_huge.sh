#!/bin/bash

echo "asymmetric low"
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix1/ -n 1
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix2/ -n 2
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix3/ -n 3
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/asymmetric_low.json ../results/low/asymmetric/mix23/ -n 1,2,3

echo "symmetric low"
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix1/ -n 1
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix2/ -n 2
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix3/ -n 3
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/symmetric_low.json ../results/low/symmetric/mix23/ -n 1,2,3



echo "asymmetric medium"
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix1/ -n 1
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix2/ -n 2
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix3/ -n 3
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/asymmetric_medium.json ../results/medium/asymmetric/mix23/ -n 1,2,3

echo "symmetric medium"
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix1/ -n 1
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix2/ -n 2
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix3/ -n 3
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/symmetric_medium.json ../results/medium/symmetric/mix23/ -n 1,2,3



echo "asymmetric high"
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix1/ -n 1
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix2/ -n 2
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix3/ -n 3
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/asymmetric_high.json ../results/high/asymmetric/mix23/ -n 1,2,3

echo "symmetric high"
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix1/ -n 1
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix2/ -n 2
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix3/ -n 3
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix12/ -n 1,2
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix13/ -n 1,3
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix23/ -n 2,3
python3 measurement.py ../cfg/symmetric_high.json ../results/high/symmetric/mix23/ -n 1,2,3
