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

The map will not be displaying at this moment. So there is also a map setup procedure

You will need to install this module that facilitate the hosting of the map.
npm install -g tileserver-gl

Theres a directory called tileserver and you'll need to cd into it and run the following command:


Finally the UI service, this is the interface folder, cd into it and install the node_modules using the package.json file
Then the UI runs by executing:

npm run serve
