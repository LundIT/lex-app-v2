#!/bin/bash

# wait for pvc to get created before running the startup script

env | grep _ >> /etc/environment

echo "analyst:$PASSWORD" | chpasswd

cd /app/DjangoProcessAdminGeneric/generic_app/submodels
git -C /app/DjangoProcessAdminGeneric/generic_app/submodels clone --recurse-submodules --depth 1 --branch $LEX_SUBMODEL_BRANCH $LEX_SUBMODEL_URL 
git config --global user.name $GIT_USERNAME
git config --global user.email $GIT_EMAIL
git config --global --add safe.directory /app/DjangoProcessAdminGeneric/generic_app/submodels/$LEX_SUBMODEL_REPO_NAME
cd /app/DjangoProcessAdminGeneric
cp .gitignore generic_app/submodels/$LEX_SUBMODEL_REPO_NAME/.gitignore
rm .gitignore

for entry in "/app/DjangoProcessAdminGeneric/generic_app/submodels/"*; do if [ -f ${entry}/requirements.txt ]; then pip install -r ${entry}/requirements.txt; fi; done

mkdir ~/.fonts
for entry in "/app/DjangoProcessAdminGeneric/generic_app/submodels/"*; do if [ -f ${entry}/fonts/*.ttf ]; then for font in "${entry}/fonts/"*; do cp ${font} ~/.fonts; done; fi; done
fc-cache -fv


if [ "$STORAGE_TYPE" = "LEGACY" ]; then
  # Since we are creating folders/files inside the volume mount directory, we need to wait for kubernetes to create
  # the mounted folder so that it has the right permissions. Removing this step causes this script to create /app/storage/uploads
  # with the containers root user, thus not allowing kubernetes to mount the volume correctly.
  while [ ! -d "/app/storage" ]; do
    echo "Waiting for volume mount to finish before editing the mount path.."
    sleep 1
  done
  echo "Volume mounted successfuly! Copying initial upload files into media root..."

  mkdir -p /app/storage/uploads
  rsync -r --exclude '.git' /app/DjangoProcessAdminGeneric/generic_app/submodels /app/storage/uploads/

fi

. /app/DjangoProcessAdminGeneric/venv/bin/activate


MIGRATION_DIR=$(find . -type d -name "migrations")

python3 manage.py makemigrations

cd $MIGRATION_DIR
if [ "$DEPLOYMENT_ENVIRONMENT" = "PROD" ]; then
    git add .
    git commit -m 'migrations file are created'
    git push
fi
cd /app/DjangoProcessAdminGeneric
build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- python3 manage.py migrate --database=$DATABASE_DEPLOYMENT_TARGET 2>&1 | tee migration-logs.txt
(python3 manage.py createsuperuser --no-input --username admin --email noreply@lund-it.com --database=default || true)

python3 manage.py createcachetable
echo "Cache backend is created."

/usr/sbin/sshd

while [ ! -d "/app/ide" ]; do
    echo "Waiting for ide volume mount to finish before editing the mount path.."
    sleep 1
done
echo "Volume mounted successfuly!"

cd ..
cp -r temp/. ide
rm -rf temp/*
ide/bin/remote-dev-server.sh registerBackendLocationForGateway

chown -R analyst:root /app/DjangoProcessAdminGeneric
chown -R analyst:root /app/ide
chown -R analyst:root /app/storage
