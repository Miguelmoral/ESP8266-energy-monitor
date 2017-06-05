#!/bin/bash

#Instalación pip
sudo apt-get install python-setuptools python-dev build-essential
sudo easy_install pip

#Instalar requirements
pip install -r requirements.txt
