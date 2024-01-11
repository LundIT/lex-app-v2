#!/bin/bash

git -C /app/DjangoProcessAdminGeneric/generic_app/submodels clone --recurse-submodules --depth 1 --branch $LEX_SUBMODEL_BRANCH $LEX_SUBMODEL_URL 

for entry in "/app/DjangoProcessAdminGeneric/generic_app/submodels/"*;
do if [ -f ${entry}/requirements.txt ]; then
  pip install -r ${entry}/requirements.txt;
  if grep -q "pytest-playwright" ${entry}/requirements.txt; then
      playwright install
  fi
fi; done

MIGRATION_DIR=$(find ./generic_app/submodels -type d -name "migrations")

yes | python manage.py makemigrations

cd $MIGRATION_DIR

if [ -n "$(git status --porcelain)" ]; then
    echo "There are new migrations"
    git config --global user.email '41898282+github-actions[bot]@users.noreply.github.com'
    git config --global user.name 'github-actions[bot]'
    git add ./*.py
    git commit -m 'New migrations file are created'
    git push
else
  echo "No new migration file";
fi

cd /app/DjangoProcessAdminGeneric/

if [ "$STORAGE_TYPE" == "LEGACY" ]; then
    # Since we are creating folders/files inside the volume mount directory, we need to wait for kubernetes to create
    # the mounted folder so that it has the right permissions. Removing this step causes this script to create /app/storage/uploads
    # with the containers root user, thus not allowing kubernetes to mount the volume correctly.
    while [ ! -d "/app/storage" ]; do
      echo "Waiting for volume mount to finish before editing the mount path.."
      sleep 1
    done

    echo "Volume mounted successfuly! Copying initial upload files into media root..."
    
    rsync -r --exclude '.git' /app/DjangoProcessAdminGeneric/generic_app/submodels /app/storage/uploads/
    echo "Initial data upload files are copied."
fi

mkdir ~/.fonts
echo "Fonts folder created."

for entry in "/app/DjangoProcessAdminGeneric/generic_app/submodels/"*; do if [ -f ${entry}/fonts/*.ttf ]; then for font in "${entry}/fonts/"*; do cp ${font} ~/.fonts; done; fi; done
fc-cache -fv
echo "Fonts configured."

build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- python manage.py migrate --database=$DATABASE_DEPLOYMENT_TARGET 2>&1 | tee migration-logs.txt
echo "Migrations applied."

(python manage.py createsuperuser --no-input --username admin --email noreply@lund-it.com --database=$DATABASE_DEPLOYMENT_TARGET || true)

python manage.py collectstatic --no-input
echo "collectstatic is successful."

python manage.py createcachetable
echo "Cache backend is created."

touch /static/index.html

echo "Now starting server..."

uvicorn --host 0.0.0.0 --port 7000 --proxy-headers --loop asyncio --reload DjangoProcessAdminGeneric.asgi:application

