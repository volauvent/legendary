#!/bin/sh
sudo pkill -f httpd



sudo rm /etc/nginx/sites-enabled/*
sudo rm /etc/nginx/sites-available/app_server_nginx.conf
sudo rm /etc/nginx/sites-available/api_server_nginx.conf
sudo cp scripts/app_server_nginx.conf /etc/nginx/sites-available/
sudo rm /etc/nginx/sites-enabled/app_server_nginx.conf
sudo ln -s /etc/nginx/sites-available/app_server_nginx.conf /etc/nginx/sites-enabled/app_server_nginx.conf
sudo service nginx restart


sudo rm -r /home/www
sudo mkdir /home/www
cd ..
sudo cp -R sedma /home/www/
cd /home/www/sedma
sudo chmod 777 server/*
sudo chmod 777 train/*
export FLASK_APP=./frontend/app/view.py

PYTHONPATH=./ python3 frontend/run.py
