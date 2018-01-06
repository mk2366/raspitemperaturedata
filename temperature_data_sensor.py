import MySQLdb
import os
import glob
import logging

# read environment to connect to a remote mariaDB
__host__ = os.environ['DB_HOST']
__user__ = os.environ['DB_USER']
__passwd__ = os.environ['DB_PASSWD']
__db__ = os.environ['DB_DB']

__sensor_files__ = []

# determine the connected sensors and store the names into __sensors__ list
try:
    # constants taken from
    # https://github.com/spotify/linux/blob/master/drivers/w1/w1_family.h
    __sensor_files__ = (glob.glob('/sys/bus/w1/devices/28-*') +
                   glob.glob('/sys/bus/w1/devices/10-*') +
                   glob.glob('/sys/bus/w1/devices/22-*'))
except:
    logging.error("Couldn't find any sensor in /sys/bus/w1/devices")
    raise
if len(__sensors__) == 0:
    logging.error("Couldn't find any sensor in /sys/bus/w1/devices")
    raise RuntimeError("Couldn't find any sensor in /sys/bus/w1/devices")
__sensor_ids__ = list(map(lamda sens: list(sens.split('-')),
                          map(os.path.basename, __sensor_files__)))

print(__sensor_ids__)
exit()

# now open connection to mariaDB where we will store the data into
# one table per w1_family
try:
    mariaDB = MySQLdb.connect(__host__, __user__, __passwd__, __db__)
except:
    raise

with mariaDB.cursor() as cur:
    # first create tables if not existant

    data = open('data','r')
    for line in data:
        time, temperature = line.split(';')
        time = str(int(float(time)))
        temperature = str(int(temperature))
        cur.execute("INSERT into measurements_28_ef972f126461 VALUES(%s, %s);" % (time, temperature))

mariaDB.commit()
mariaDB.close()
