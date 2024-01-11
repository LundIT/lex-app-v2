#!/bin/bash

git -C /app/DjangoProcessAdminGeneric/generic_app/submodels clone --recurse-submodules --depth 1 --branch $LEX_SUBMODEL_BRANCH $LEX_SUBMODEL_URL

for entry in "/app/DjangoProcessAdminGeneric/generic_app/submodels/"*;
do if [ -f ${entry}/requirements.txt ]; then
  pip install -r ${entry}/requirements.txt;
fi; done

cd /app/DjangoProcessAdminGeneric/

build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- celery -A DjangoProcessAdminGeneric  worker -l info --concurrency=4 --prefetch-multiplier=1