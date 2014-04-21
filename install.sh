sudo apt-get install npm
sudo npm install yo bower grunt-cli
sudo npm install -g generator-webapp

# Init sqlite database
python ./src/db.py

# Run server
grunt serve