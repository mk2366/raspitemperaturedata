import MySQLdb
import os

__host__ = os.environ['DB_HOST']
__user__ = os.environ['DB_USER']
__passwd__ = os.environ['DB_PASSWD']
__db__ = os.environ['DB_DB']


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
    


