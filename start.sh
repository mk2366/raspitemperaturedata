#!/bin/bash

me=`realpath $0`
base=`dirname $me`
dat=`date`

cd $base

mv nohup.out "nohup.out$dat"
nohup pipenv run ./temperature_data_sensor.py &
