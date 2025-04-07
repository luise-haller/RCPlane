# RCPlane
Scripts used in congruence with the RC Plane Wildfire Prediction System Modeling Project to read sensor data, receiver/transceiver, automation for proper flight.

    Read and log sensor data (e.g., temperature, humidity, GPS)
    Communicate with the RC receiver/transceiver
    Automate and manage proper flight behavior


# Requirements
Before running the project, make sure you have the following installed:
- Raspberry Pi (any model with GPIO support)
- Raspbian OS Lite
- Python3
  
# Packages
- import RPi.GPIO
- import time
- import datetime
- import os
- import subprocess
