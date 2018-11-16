#!/bin/bash
# Change permissions to something that SSH accepts
chmod 600 deploy/deploy_key;
# Send the commit hash env variable over ssh to know which commit to checkout to
export LC_COMMIT_HASH="$TRAVIS_COMMIT"
# Pipe the update script over SSH to the production server
chmod +x deploy/update_app.sh && cat deploy/update_app.sh | ssh -o StrictHostKeyChecking=no -o BatchMode=yes \
-o SendEnv=LC_COMMIT_HASH -i deploy/deploy_key "$DEPLOY_USER@$DEPLOY_SERVER"