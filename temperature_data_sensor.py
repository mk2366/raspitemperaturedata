#!/usr/bin/env python
"""
Temperature Sensor Script.

This python script is used to read temperature sensors on the 1wire bus
of the raspberry pi and send the data to a mysql db
"""

import MySQLdb
import os
import glob
import logging
import time
import threading
import shutil
import signal

__kill__ = False


def safe_panic():
    import pickle
    global __db_commands_buffer
    with open(__panic_file__, 'wb') as f:
        pickle.dump(__db_commands_buffer, f)
    global __kill__
    __kill__ = True


# Want to safe the data when program is killed
signal.signal(signal.SIGINT, safe_panic)
signal.signal(signal.SIGTERM, safe_panic)


def touch(path):
    """
    Unix touch().

    Copied from http://code.activestate.com/recipes/576915-touch/
    """
    now = time.time()
    try:
        # assume it's there
        os.utime(path, (now, now))
    except os.error:
        # if it isn't, try creating the directory,
        # a file with that name
        open(path, "w").close()
        os.utime(path, (now, now))


# read environment to connect to a remote mariaDB
__host__ = os.environ['DB_HOST']
__user__ = os.environ['DB_USER']
__passwd__ = os.environ['DB_PASSWD']
__db__ = os.environ['DB_DB']

__db_commands_buffer = []

__sensor_files__ = []
__panic_file__ = (os.path.dirname(os.path.abspath(__file__)) +
                  "/dbcommands.panic")
__watchdog_file__ = (os.path.dirname(os.path.abspath(__file__)) +
                     "/watchdog")

def db_connectivity():
    """
    Now open connection to mariaDB.

    Here we are going to store into
    one table per w1_family.
    """
    global __db_commands_buffer
    try:
        mariaDB = MySQLdb.connect(__host__, __user__, __passwd__, __db__)
    except:
        vt = time.asctime()
        logging.error('%s: DB connectivity not given. Retry in 10 minutes.'
                      % (vt,))
    else:
        try:
            cur = mariaDB.cursor()
        except Exception:
            import traceback
            logging.error(traceback.format_exc())
            logging.error("%s: Couldn't get cursor. DB connection is available"
                          % (time.asctime(),))
        else:
            try:
                for execute_string in __db_commands_buffer:
                    cur.execute(execute_string)
            except Exception:
                import traceback
                logging.error(traceback.format_exc())
                logging.error("%s: Cursor avail but couldn't \
                              exec this inserts:\n%s"
                              % (time.asctime(), execute_string))
                mariaDB.rollback()
            else:
                __db_commands_buffer = []
                mariaDB.commit()
            finally:
                mariaDB.close()
                vt = time.asctime()
                logging.info('%s: DB connected successfully.' % (vt,))
    finally:
        threading.Timer(600, db_connectivity).start()


threading.Timer(600, db_connectivity).start()

try:
    f = open(__panic_file__, 'rb')
    import pickle
    __db_commands_buffer = pickle.load(f)
    f.close()
    shutil.move(__panic_file__, __panic_file__ + str(time.time()))
except:
    # nothing was saved in panic: good
    pass


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


for family in set(x[0] for x in __sensor_ids__):
    execute_string = "CREATE TABLE IF NOT EXISTS %s\
                (id VARCHAR(64),\
                t bigint,\
                temperature int)" % ('t' + family,)
    __db_commands_buffer += [execute_string]

try:
    while not __kill__:
        for sensor_file in __sensor_files__:
            f = open(sensor_file + "/w1_slave", "r")
            f_cont = f.read()
            f.close()
            temp_index = f_cont.find("t=")
            db_tuple = (time.time(), int(f_cont[temp_index+2:temp_index+7]))
            fam, id = (os.path.basename(sensor_file)).split("-")
            value_string = "VALUE ('%s', %i, %i)" % (((id,) + db_tuple))
            execute_string = ("INSERT INTO %s (id, t, temperature) %s" %
                              ('t'+fam, value_string))
            __db_commands_buffer += [execute_string]
        touch(__watchdog_file__)
        time.sleep(60)
except:
    import pickle
    with open(__panic_file__, 'wb') as f:
        pickle.dump(__db_commands_buffer, f)
    raise
