FROM python:3.11-slim

ENV TZ=America/New_York

# Install cron and timezone data
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for persistent configuration and state
RUN mkdir -p /data

WORKDIR /app

# Copy application code
COPY daily.py /app/

# Copy default config into the data volume
COPY config.json /data/

# Expose /data as a volume for asked_questions.json and config.json
VOLUME ["/data"]

# Install runtime dependencies
RUN pip install --no-cache-dir requests

# Schedule the script to run at 9AM Mon-Fri
RUN echo "0 9 * * 1-5 root cd /app && /usr/local/bin/python /app/daily.py >> /var/log/cron.log 2>&1" \
        > /etc/cron.d/daily_code_question \
    && chmod 0644 /etc/cron.d/daily_code_question \
    && crontab /etc/cron.d/daily_code_question \
    && touch /var/log/cron.log

CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]