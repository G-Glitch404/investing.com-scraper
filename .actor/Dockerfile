FROM apify/actor-python:3.11

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apt-get update \
 && apt-get install -y --no-install-recommends wget ca-certificates gnupg unzip xvfb \
    fonts-liberation libnss3 libgconf-2-4 libxss1 libappindicator3-1 \
    libatk-bridge2.0-0 libgtk-3-0 libasound2 libx11-xcb1 libxtst6 libdbus-glib-1-2 \
 && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends google-chrome-stable \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY src .logs .data_dirs /usr/src/app/

RUN python3 -m compileall -q .

ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome-stable

CMD ["python3", "-m", "src"]
