#!/bin/bash
# apt-get update
# apt-get install -y wget unzip
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# apt-get install -y ./google-chrome-stable_current_amd64.deb

#!/bin/bash
# pip install -r requirements.txt

#!/bin/bash
# Make sure we have the latest pip
pip install --upgrade pip

# Install numpy first to avoid compatibility issues
pip install numpy==1.26.3

# Then install the rest of the requirements
pip install -r requirements.txt

# Make scripts executable
chmod +x start.sh