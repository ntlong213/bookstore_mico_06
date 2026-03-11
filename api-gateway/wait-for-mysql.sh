#!/bin/bash
set -e

host="$1"
shift
cmd="$@"

echo "Waiting for MySQL at $host..."
until nc -z "${host%:*}" "${host##*:}"; do
  >&2 echo "MySQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "MySQL is up - executing command"
exec $cmd
