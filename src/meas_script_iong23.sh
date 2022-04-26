#!/bin/bash

echo "asymmetric low"
python3 measurement.py ../cfg/asymmetric_low.json ../results/asymmetric_low_mix23/
echo "asymmetric medium"
python3 measurement.py ../cfg/asymmetric_medium.json ../results/asymmetric_medium_mix23/
echo "asymmetric high"
python3 measurement.py ../cfg/asymmetric_high.json ../results/asymmetric_high_mix23/

echo "symmetric low"
python3 measurement.py ../cfg/symmetric_low.json ../results/symmetric_low_mix23/
echo "symmetric medium"
python3 measurement.py ../cfg/symmetric_medium.json ../results/symmetric_medium_mix23/
echo "symmetric high"
python3 measurement.py ../cfg/symmetric_high.json ../results/symmetric_high_mix23/
