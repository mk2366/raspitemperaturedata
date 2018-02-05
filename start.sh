#!/bin/bash

me=`realpath $0`
base=`dirname $me`
dat=`date`

cd $base
nohup pipenv run ./temperature_data_sensor.py &
