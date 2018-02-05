#!/usr/bin/env bash

me=`realpath $0`
base=`dirname $me`
dat=`date`

cd $base
echo `pwd`
mv nohup.out "nohup.out$dat"
nohup pipenv run ./temperature_data_sensor.py &
