# raspitemperaturedata

__Don't read on. This project is in beginning phase!__

Small python project to collect temperature data via a DS18B20 connected to a Raspberry Pi.
The data will be collected on a server using [MariaDB](http://mariadb.org/).

Important:
sudo apt-get install libmariadbclient-dev
before
pipenv install mysqlclient

Hint:
shell> mysqldump [options] db_name [tbl_name ...]
shell> mysqldump [options] --databases db_name ...
shell> mysqldump [options] --all-databases

Crontab:
@reboot . /etc/profile; . $HOME/.profile; /home/pi/production/raspitemperaturedata/start.sh >> /home/pi/production/raspitemperaturedata/log.out 2>&1
