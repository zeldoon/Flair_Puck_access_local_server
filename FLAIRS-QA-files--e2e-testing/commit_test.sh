#!/bin/bash
set +x

exitcode=0
changed_tests=$(git diff-index --cached HEAD | awk '{print $6}' | grep '/test_.*\.py')
echo $changed_tests

if [[ $changed_tests != "" ]]; then
    if [[ $changed_tests == *"feature/"* && $TEST_ENV != 'dev' ]]; then
        perl -pi -e 's/"headless":\s+false/"headless": true/g' feature/settings.json
        PGUSER=flair PGPASSWORD=$(cat ft_pass) PGHOST=flair-ft-aurora.cluster-cfkoqjoirj4p.us-east-1.rds.amazonaws.com PGPORT=5432 PGDATABASE=flair_ft ./db_reset.sh
    fi
    for test in $changed_tests; do
        if [[ $test != *"delayed_tests/"* && -f $test ]]; then
            pytest -vsx $test
            exitcode=$((exitcode+$?))
        fi
    done
    git checkout feature/settings.json
fi

exit $exitcode
