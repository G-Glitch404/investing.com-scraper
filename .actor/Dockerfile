FROM apify/actor-python-selenium

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN mkdir -p logs .db .data_dirs
RUN python3 -m compileall -q .

ENV DISPLAY=:99

CMD ["python3", "-m", "src"]
