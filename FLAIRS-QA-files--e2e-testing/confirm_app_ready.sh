#!/bin/bash

ITERS=0
while [[ $(pg_isready) = *"reject"* ]]; do
    if (( ITERS > 20 )); then
        echo "DB pop failed to complete in 100s"
        exit 1
    fi
    sleep 5
    ITERS=$((ITERS+1))
done
echo "DB pop complete"

ITERS=0
while [[ $(curl -L -s -o /dev/null -w "%{http_code}" "my-ft.flair.co/${PR_BRANCH_NAME}") != '200' ]]; do
    if (( ITERS > 20 )); then
        echo "UI failed to be ready in 100s"
        exit 1
    fi
    sleep 5
    ITERS=$((ITERS+1))
done
echo "UI is ready"