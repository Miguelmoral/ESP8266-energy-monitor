
#!/bin/bash

#Instalación git y pip

sudo apt-get install git
sudo apt-get install python-setuptools python-dev build-essential
sudo easy_install pip

#Descarga requirements.txt desde github e instalación requirements

wget https://raw.githubusercontent.com/miguelmoral/ESP8266-energy-monitor/master/requirements.txt
pip install -r requirements.txt

# Clonar repo de github
sudo git clone https://github.com/Miguelmoral/ESP8266-energy-monitor

# Incluir el script para lanzar la web en init.d para ejecutar automaticamente al inicio

cd ESP8266-energy-monitor/web
python main.py &
