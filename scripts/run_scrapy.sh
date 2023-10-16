#!/bin/bash


if [ -z "$APP_HOME" ]; then
  echo "The APP_HOME environment variable is not set"
  exit 1
fi

cd "$APP_HOME"

/usr/local/bin/scrapy crawl autoria
