#!/bin/bash

cd /vscode/DjangoProcessAdminGeneric/generic_app/submodels
git clone --recurse-submodules --branch $LEX_SUBMODEL_BRANCH $LEX_SUBMODEL_URL
git config --global user.name $GIT_USERNAME
git config --global user.email $GIT_EMAIL
cp .gitignore $LEX_SUBMODEL_REPO_NAME/.gitignore
rm .gitignore

cd /vscode/DjangoProcessAdminGeneric
for entry in "/vscode/DjangoProcessAdminGeneric/generic_app/submodels/"*; do if [ -f ${entry}/requirements.txt ]; then pip install -r ${entry}/requirements.txt; fi; done

mkdir ~/.fonts
for entry in "/vscode/DjangoProcessAdminGeneric/generic_app/submodels/"*; do if [ -f ${entry}/fonts/*.ttf ]; then for font in "${entry}/fonts/"*; do cp ${font} ~/.fonts; done; fi; done
fc-cache -fv

MIGRATION_DIR=$(find . -type d -name "migrations")

python3 manage.py makemigrations
cd $MIGRATION_DIR
if [ "$DEPLOYMENT_ENVIRONMENT" = "PROD" ]; then
    git add .
    git commit -m 'migrations file are created'
    git push
fi
cd /vscode/DjangoProcessAdminGeneric
build/wait-for-it.sh -t 60 $DATABASE_DOMAIN:5432 -- python3 manage.py migrate --database=$DATABASE_DEPLOYMENT_TARGET 2>&1 | tee migration-logs.txt
(python3 manage.py createsuperuser --no-input --username admin --email noreply@lund-it.com --database=default || true)


python3 manage.py collectstatic --no-input

touch /static/index.html

sed -i "s/password:.*/password: $PASSWORD/" ~/.config/code-server/config.yaml







