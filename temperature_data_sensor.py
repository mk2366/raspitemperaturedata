import MySQLdb
import os
import glob
import logging

# read environment to connect to a remote mariaDB
__host__ = os.environ['DB_HOST']
__user__ = os.environ['DB_USER']
__passwd__ = os.environ['DB_PASSWD']
__db__ = os.environ['DB_DB']

__sensors__ = []

# determine the connected sensors and store the names into __sensors__ list
try:
    # constants taken from
    # https://github.com/spotify/linux/blob/master/drivers/w1/w1_family.h
    __sensors__ = (glob.glob('/sys/bus/w1/devices/28-*') +
                   glob.glob('/sys/bus/w1/devices/10-*') +
                   glob.glob('/sys/bus/w1/devices/22-*'))
except:
    logging.error("Couldn't find any sensor in /sys/bus/w1/devices")
    raise
if len(__sensors__) == 0:
    logging.error("Couldn't find any sensor in /sys/bus/w1/devices")
    raise RuntimeError("Couldn't find any sensor in /sys/bus/w1/devices")

print __sensors__
exit()


try:
    mariaDB = MySQLdb.connect(__host__, __user__, __passwd__, __db__)
except:
    raise

with mariaDB.cursor() as cur:
    data = open('data','r')
    for line in data:
        time, temperature = line.split(';')
        time = str(int(float(time)))
        temperature = str(int(temperature))
        cur.execute("INSERT into measurements_28_ef972f126461 VALUES(%s, %s);" % (time, temperature))

mariaDB.commit()
mariaDB.close()
