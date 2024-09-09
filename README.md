# Astroguard
This is the repository for all Astroguard code

Theres a few sections to this repo:

1) The command centre files
2) The ESP32 boards projects (LoRaReceiver, SB1/TinyGPS_Example, SB2/TinyGPS_Example)
3) The AI CCTV code files

The command centre makes use of a local mongodb instance at localhost:27017
To run the flask server first you need to cd into the server directory then,
you simply need to activate the local venv enviroment.

Then install the required packages using the requirements.txt file.
You may then run the flask server by executing:

python ./app.py

Tests can be run by executing this command:

python ./tests.py

The map will not be displaying at this moment. So there is also a map setup procedure

You will need to install this module that facilitate the hosting of the map.
npm install -g tileserver-gl

You must download the tileserver from my google drive as github doesn't allow uploads of large files:
https://drive.google.com/drive/folders/1jgaGlPU7mm3kZvkFpO1aBx46c5OBSf45?usp=sharing

Just cd into it and run the following command to initialize the map:
tileserver-gl-light --config config.json --verbose -p 8000

Next the UI service, this is the interface folder, cd into it and install the node_modules using the package.json file
Then the UI runs by executing:

npm run serve

And finally to test the AI CCTV camera you need to activate the venv using source cam/bin/activate
Then you may install the packages by using the requirements.txt file once that it done you can
run the program by executing python detect.py
