FROM python:3.6-stretch

# Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get install -y git

# Install digestiflow-server and dependencies through pip.  Then, migrate
# and create the sueruser account.
RUN git clone https://github.com/bihealth/digestiflow-server.git /app
RUN pip install -r /app/requirements/production.txt
