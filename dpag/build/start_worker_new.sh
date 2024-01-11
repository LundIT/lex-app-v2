#!/bin/bash

cd /app/DjangoProcessAdminGeneric/
build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- celery -A DjangoProcessAdminGeneric  worker -l info --concurrency=4 --prefetch-multiplier=1
