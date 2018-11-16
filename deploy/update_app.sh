#!/bin/bash
TARGET="${LC_COMMIT_HASH:-origin/master}"
. .bashrc
APP_DIR=~/pur_beurre_web/
cd "$APP_DIR"
echo "# Starting deployment."
echo "# Target commit: ${TARGET}"
set -e # Fail the script on any errors.

echo "# Stashing local changes to tracked files."
git stash
echo "# Fetching remote."
git fetch --all
echo "# Checking out the specified commit."
git checkout "${TARGET}"
make docker-deploy
echo "# Deployment done!"