install:
	sudo apt-get install python-setuptools python-dev build-essential && sudo easy_install pip && pip install -r requirements.txt  

ejecutar:
	cd web && python main.py
