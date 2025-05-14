FROM python:3.11-slim

ENV TZ=America/New_York

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY daily.py config.json ./

RUN pip install --no-cache-dir requests

RUN echo "0 9 * * 1-5 root cd /app && /usr/local/bin/python daily.py >> /var/log/cron.log 2>&1" \
        > /etc/cron.d/daily_code_question \
    && chmod 0644 /etc/cron.d/daily_code_question \
    && crontab /etc/cron.d/daily_code_question \
    && touch /var/log/cron.log

CMD ["sh", "-c", "/usr/local/bin/python /app/daily.py && cron && tail -f /var/log/cron.log"]
