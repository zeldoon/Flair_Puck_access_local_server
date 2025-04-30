#!/bin/bash +x

if [ -z "$PR_BRANCH_NAME" ] || [ "$PR_BRANCH_NAME" = 0 ]; then
    echo "PR_BRANCH_NAME not set"
    exit 0
fi

perl -pi -e "s/(my-.*flair.co)/\$1\/${PR_BRANCH_NAME}/g" feature/env.json
