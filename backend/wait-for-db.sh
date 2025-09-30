#!/bin/sh
set -e

host="$1"
shift
cmd="$@"

export PGPASSWORD=$POSTGRES_PASSWORD

until psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Banco não disponível, tentando novamente em 2s..."
  sleep 2
done

>&2 echo "Banco disponível!"
exec $cmd
