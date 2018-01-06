import time

while True:
    devicefile = open("/sys/bus/w1/devices/28-ef972f126461/w1_slave")
    devicefilecontent = devicefile.read()
    devicefile.close()
    index = devicefilecontent.find("t=")
    with open('data','a') as d:
        d.write(str(time.time())+'; ' + devicefilecontent[index+2:index+7] + '\n')
    time.sleep(60)

