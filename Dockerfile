# # FROM docker/whalesay:latest
# # LABEL Name=seleniumhostingcheck Version=0.0.1
# # RUN apt-get -y update && apt-get install -y fortunes
# # CMD ["sh", "-c", "/usr/games/fortune -a | cowsay"]

# FROM python:3.10-slim

# # Install Chrome and dependencies
# RUN apt-get update && apt-get install -y \
#     wget \
#     gnupg \
#     unzip \
#     xvfb \
#     libxi6 \
#     libgconf-2-4 \
#     default-jdk \
#     curl

# # Install Google Chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
#     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
#     && apt-get update \
#     && apt-get install -y google-chrome-stable

# # Install ChromeDriver
# RUN CHROME_VERSION=$(google-chrome --version | awk -F '[ .]' '{print $3"."$4"."$5}') \
#     && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
#     && wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
#     && unzip chromedriver_linux64.zip \
#     && mv chromedriver /usr/bin/chromedriver \
#     && chmod +x /usr/bin/chromedriver

# # Set working directory
# WORKDIR /app

# # Copy requirements and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY app.py .

# # Expose port
# EXPOSE 8080

# # Start command
# CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]


FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libgconf-2-4 \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | cut -d ' ' -f 3 | cut -d '.' -f 1) \
    && wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O - > CHROMEDRIVER_VERSION \
    && wget -q "https://chromedriver.storage.googleapis.com/$(cat CHROMEDRIVER_VERSION)/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip CHROMEDRIVER_VERSION

# Install dependencies in the correct order
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir numpy==1.26.3 \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
