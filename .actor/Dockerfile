FROM apify/actor-python-seleniumDebian:latest

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY .db ./.db

RUN mkdir -p logs .data_dirs

RUN python3 -m compileall -q .

RUN cat >/usr/local/bin/entrypoint.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from seleniumbase import Driver

driver = Driver(uc=True, headless=True, disable_gpu=True)
driver.quit()
PY

exec python3 -m src
SH

RUN chmod +x /usr/local/bin/entrypoint.sh

CMD ["/usr/local/bin/entrypoint.sh"]
