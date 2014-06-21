sudo apt-get install npm nodejs
sudo npm install yo bower grunt-cli grunt
sudo npm install -g generator-webapp

sudo chmod 777 -R ~/tmp

sudo ln /usr/bin/nodejs /usr/bin/node

npm install

bower install

# Init dev sqlite database
python ./src/modles.py

# Init npm local package
sudo npm install
sudo pip install -r requeiments.pip
# Run server
grunt serve

