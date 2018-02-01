#!/bin/bash

cd ~/dev/raspitemperaturedata
pipenv shell
nohup python temperature_data_sensor.py &
