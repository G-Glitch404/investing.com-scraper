FROM apify/actor-python-selenium

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY src ./src
COPY .db ./.db

RUN pip install --no-cache-dir -r requirements.txt


RUN mkdir -p logs .db .data_dirs
RUN python3 -m compileall -q .

ENV DISPLAY=:99

CMD ["python3", "-m", "src"]
