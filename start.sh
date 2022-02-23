#!/bin/bash 

# turn the power LED off
echo 0 | sudo tee /sys/class/leds/led1/brightness > /dev/null


python3 sense.py