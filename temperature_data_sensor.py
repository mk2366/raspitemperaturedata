import MySQLdb
import os
import glob
import logging
import time

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
if len(__sensor_files__) == 0:
    logging.error("Couldn't find any sensor in /sys/bus/w1/devices")
    raise RuntimeError("Couldn't find any sensor in /sys/bus/w1/devices")
__sensor_ids__ = list(map(lambda sens: list(sens.split('-')),
                          map(os.path.basename, __sensor_files__)))

# now open connection to mariaDB where we will store the data into
# one table per w1_family
try:
    mariaDB = MySQLdb.connect(__host__, __user__, __passwd__, __db__)
except:
    raise

with mariaDB.cursor() as cur:
    for family in set(x[0] for x in __sensor_ids__):
        cur.execute("CREATE TABLE IF NOT EXISTS %s\
                    (id VARCHAR(64),\
                    t bigint,\
                    temperature int,\
                    user VARCHAR(256))" % ('t' + family))
mariaDB.commit()

while True:
    for sensor_file in __sensor_files__:
        f = open(sensor_file + "/w1_slave", "r")
        f_cont = f.read()
        f.close()
        temp_index = f_cont.find("t=")
        db_tuple = (time.time(), int(f_cont[temp_index+2:temp_index+7]))
        fam, id = (os.path.basename(sensor_file)).split("-")
        value_string = "VALUE ('%s', %i, %i, '%s')" % (((id,) + db_tuple)
                                                       + (__user__,))
        with mariaDB.cursor() as cur:
            cur.execute("INSERT INTO %s %s" % ('t'+fam, value_string))
    mariaDB.commit()
    time.sleep(60)

mariaDB.close()
