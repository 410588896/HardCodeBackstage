#! /bin/bash
uwsgi --ini /home/HardCodeBackstage/uwsgi/uwsgi.ini
ps aux | grep uwsgi | grep -v grep
