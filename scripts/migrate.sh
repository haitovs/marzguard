#!/bin/bash
set -e
cd "$(dirname "$0")/.."
alembic upgrade head
echo "Migrations complete."
