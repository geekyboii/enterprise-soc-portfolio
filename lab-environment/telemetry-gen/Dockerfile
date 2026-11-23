FROM python:3.12-alpine

RUN apk add --no-cache openssh-client sshpass curl && \
    mkdir -p /var/log/corp /app

WORKDIR /app
COPY telemetry.py /app/telemetry.py

CMD ["python3", "-u", "/app/telemetry.py", "daemon"]
