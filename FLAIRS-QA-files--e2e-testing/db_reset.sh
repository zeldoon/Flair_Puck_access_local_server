#!/bin/bash -x

i=0
RESET_DB=$(psql -P pager=off -c 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '"'${PGDATABASE}'"' AND pid <> pg_backend_pid();')
while [[ $RESET_DB = *"(0 rows)"* ]]; do
  sleep 10
  if [ $i = '12' ]; then
    echo "failed to terminate postgres backend"
    exit 1
  fi
  i=$(( $i + 1 ))
  RESET_DB=$(psql -P pager=off -c 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '"'${PGDATABASE}'"' AND pid <> pg_backend_pid();')
done

i=0
DROP_DB=$(psql -d postgres -c "DROP DATABASE ${PGDATABASE};" 2>&1)
while [[ $DROP_DB = *"being accessed by other users"* ]]; do
  sleep 10
  if [ $i = '12' ]; then
    echo "failed to drop database; db in use"
    exit 1
  fi
  i=$(( $i + 1 ))
  RESET_DB=$(psql -P pager=off -c 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '"'${PGDATABASE}'"' AND pid <> pg_backend_pid();')
  DROP_DB=$(psql -d postgres -c "DROP DATABASE ${PGDATABASE};" 2>&1)
done

psql -d postgres -c "CREATE DATABASE ${PGDATABASE} WITH ENCODING 'UTF-8';"
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${PGDATABASE} TO ${PGUSER};"
psql -q -f test_db.sql > /dev/null
if [[ $(psql -P pager=off -c "SELECT id, name FROM structure WHERE id = '4';") = *"expired"* ]]; then
  echo "db loaded to FT env successfully"
else
  echo "db failed to load to FT env"
  exit 1
fi
