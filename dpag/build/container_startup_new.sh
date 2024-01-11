#!/bin/bash

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

build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- python manage.py migrate --database=$DATABASE_DEPLOYMENT_TARGET 2>&1 | tee migration-logs.txt

(python manage.py createsuperuser --no-input --username admin --email noreply@lund-it.com --database=$DATABASE_DEPLOYMENT_TARGET || true)

python manage.py collectstatic --no-input
echo "collectstatic is successful."

python manage.py createcachetable
echo "Cache backend is created."

touch /static/index.html

echo "Now starting server..."

uvicorn --host 0.0.0.0 --port 7000 --proxy-headers --loop asyncio --reload DjangoProcessAdminGeneric.asgi:application

