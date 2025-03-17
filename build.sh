#!/bin/bash
# apt-get update
# apt-get install -y wget unzip
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# apt-get install -y ./google-chrome-stable_current_amd64.deb

#!/bin/bash
# pip install -r requirements.txt

#!/bin/bash
# # Make sure we have the latest pip
# pip install --upgrade pip

# # Install numpy first to avoid compatibility issues
# pip install numpy==1.26.3

# # Then install the rest of the requirements
# pip install -r requirements.txt

# # Make scripts executable
# chmod +x start.sh

# apt-get update && \
# apt-get install -y wget gnupg unzip && \
# wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
# echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
# apt-get update && \
# apt-get install -y google-chrome-stable && \
# CHROME_VERSION=$(google-chrome-stable --version | cut -d ' ' -f 3 | cut -d '.' -f 1) && \
# wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O CHROMEDRIVER_VERSION && \
# wget -q "https://chromedriver.storage.googleapis.com/$(cat CHROMEDRIVER_VERSION)/chromedriver_linux64.zip" && \
# unzip chromedriver_linux64.zip && \
# mv chromedriver /usr/bin/chromedriver && \
# chmod +x /usr/bin/chromedriver && \

set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Chrome"
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # Make sure we return to where we were
else
  echo "...Using Chrome from cache"
fi
pip install -r requirements.txt