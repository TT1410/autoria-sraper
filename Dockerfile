FROM python:3.11

ENV APP_HOME /app
ENV DIR_DUMPS $APP_HOME/dumps

COPY . $APP_HOME

WORKDIR $APP_HOME


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install cron && apt-get -y install postgresql-client


RUN echo "0 12 * * * /bin/bash $APP_HOME/scripts/run_scrapy.sh > /var/log/cron_scrapy.log 2>&1" >> /etc/cron.d/cronfile
RUN echo "0 0 * * * /bin/bash $APP_HOME/scripts/pg_dump.sh > /var/log/cron_dump.log 2>&1" >> /etc/cron.d/cronfile


RUN chmod 0644 /etc/cron.d/cronfile
RUN crontab /etc/cron.d/cronfile

ENTRYPOINT ["/bin/bash", "/app/scripts/entrypoint.sh"]
