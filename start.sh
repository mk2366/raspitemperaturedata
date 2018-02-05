#!/bin/bash

me=`realpath $0`
base=`dirname $me`
dat=`date`

cd $base
<<<<<<< HEAD
mv nohup.out "nohup.out$dat"
=======
mv nohup.out "nohup.out"$dat
>>>>>>> ee28b09df8b9a8be19c7a1eb54b4e51d50c0008e
nohup pipenv run ./temperature_data_sensor.py &
