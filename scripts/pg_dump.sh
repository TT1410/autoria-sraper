#!/bin/bash

if [ -z "$DATABASE_URL" ]; then
  echo "The DATABASE_URL variable is not set!"
  exit 1
fi

if [ -z "$DIR_DUMPS" ]; then
  echo "The DIR_DUMPS variable is not set!"
  exit 1
fi

backup_filename="$DIR_DUMPS/backup_$(date +\%Y_\%m_\%d).sql"

pg_dump --dbname "$DATABASE_URL" > "$backup_filename"

if [ $? -eq 0 ]; then
  echo "Backup successfully created in: $backup_filename"
else
  echo "Error creating database dump!"
fi