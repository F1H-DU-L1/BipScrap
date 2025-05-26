# Select lightweight Python image
FROM python:3.11-slim

# Install wget, curl, unzip
RUN apt update && apt install -y wget curl unzip jq netcat-openbsd

# Download and install google chrome
RUN wget -q -O chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./chrome.deb \
    && rm chrome.deb

# Get google-chrome version
RUN GOOGLE_CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    echo "✅ Zainstalowana wersja Chrome: $GOOGLE_CHROME_VERSION"

# Download proper chrome driver
# Pobranie odpowiedniej wersji ChromeDriver
RUN GOOGLE_CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROMEDRIVER_URL=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | \
    jq -r --arg CHROME_VERSION "$GOOGLE_CHROME_VERSION" '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url') && \
    wget -q -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 && \
    chmod +x /usr/local/bin/chromedriver

# Skopiowanie skryptu wait-for-it.sh
COPY ../../wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Set workdir
WORKDIR /app

# Copy requirements file
COPY services/data_acquisition/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY services/data_acquisition/ .


# Run application
CMD ["wait-for-it.sh", "rabbitmq:5672", "-t", "30", "--", "python", "webscrapping.py"]