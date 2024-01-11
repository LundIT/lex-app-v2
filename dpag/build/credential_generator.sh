#!/bin/bash
if kubectl get secret -n $K8S_NAMESPACE $DATABASE_SECRET_NAME &> /dev/null; then
  exit 0
else
  echo "Credentials secret does not exist"
  USERNAME=$({ echo "user"; eval date +'%s'; eval qrandom --int --min 1000000 --max 9999999 | tr -dc '0-9' | head -c 5; } | tr "\n" "1")
  PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9!=?:;' | head -c 30)
  psql "host=$DATABASE_DOMAIN port=5432 dbname=postgres user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY" -c "DROP USER IF EXISTS $USERNAME;"
  psql "host=$DATABASE_DOMAIN port=5432 dbname=postgres user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY" -c "CREATE USER $USERNAME WITH PASSWORD '$PASSWORD';"
  (psql "host=$DATABASE_DOMAIN port=5432 dbname=postgres user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY " -c "CREATE DATABASE $DATABASE_NAME;" || true)
  OWNER_DB=$(psql -tA "host=$DATABASE_DOMAIN port=5432 dbname=postgres user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY" -c "SELECT pg_catalog.pg_get_userbyid(d.datdba) as \"Owner\" FROM pg_catalog.pg_database d WHERE d.datname = '$DATABASE_NAME' ORDER BY 1;")
  psql "host=$DATABASE_DOMAIN port=5432 dbname=$DATABASE_NAME user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY" -c "GRANT $USERNAME TO initdeploy; ALTER DATABASE $DATABASE_NAME OWNER TO $USERNAME;"
  kubectl create secret -n $K8S_NAMESPACE generic $DATABASE_SECRET_NAME --from-literal="username=$USERNAME" --from-literal="password=$PASSWORD"
  ### Edge case. Database of the PROD and TEST environments have two database users for some reason: inideploy and lexictechnical1 
  if [ $DEPLOYMENT_ENVIRONMENT != "DEV" ]; then
    psql "host=$DATABASE_DOMAIN port=5432 dbname=$DATABASE_NAME user=initdeploy password=$POSTGRES_PASSWORD_INITDEPLOY" -c "GRANT $USERNAME TO lexictechnical1; REASSIGN OWNED BY $OWNER_DB TO $USERNAME;"
  fi
fi

