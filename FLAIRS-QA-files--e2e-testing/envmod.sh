#!/bin/bash

cp setup_process/env_example.json setup_process/env.json
perl -pi -e "s/__FLAIR_USERNAME/${FLAIR_USR}/g" setup_process/env.json
perl -pi -e "s/__FLAIR_PASSWORD/${FLAIR_PSW}/g" setup_process/env.json
perl -pi -e "s/__ECOBEE_USERNAME/${ECOBEE_USR}/g" setup_process/env.json
perl -pi -e "s/__ECOBEE_PASSWORD/${ECOBEE_PSW}/g" setup_process/env.json
perl -pi -e 's/"headless":\s+false/"headless": true/g' setup_process/settings.json
perl -pi -e 's/"headless":\s+false/"headless": true/g' hardware/settings.json
