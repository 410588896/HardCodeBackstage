#! /bin/bash
uwsgi --stop /home/HardCodeBackstage/script/uwsgi.pid 
sleep 1
uwsgi --ini /home/HardCodeBackstage/uwsgi/uwsgi.ini
sleep 1
ps aux | grep uwsgi | grep -v grep
