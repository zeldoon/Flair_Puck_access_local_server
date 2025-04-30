#!/bin/sh
if [ "$#" -ne 2 ] && [ "$#" -ne 3 ]; then
    echo "./puck-api.sh [command] {...args}"
    echo "-- Commands {...args} --"
    echo "get_access_token {client_id} {client_secret}"
    echo "post_puck_status {auth_token}"
    echo "confirm_puck_ir_codes_download {auth_token}"
    exit 0
fi

#PUCK_ID="7a04d15b-088c-5215-f666-18b30254749b"
PUCK_ID="d58ea125-f573-5b7d-6c8b-577304f1a644"
DESIRED_STATE_ID="37f0" # first four characters of puck state ID
#TODO
API_ROOT="https://api-qa.flair.co/"
VERSION=8
AUTH_TOKEN=$2
CLIENT_ID=$2
CLIENT_SECRET=$3

case $1 in
    "get_access_token") curl \
                        -H "Content-Type: application/x-www-form-urlencoded" \
                        -H "Accept: application/json" \
                        -H "User-Agent: Flair Puck 1.0" \
                        -d "grant_type=client_credentials&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET" \
                        "${API_ROOT}oauth/token" ;;

    "post_puck_status") curl \
                    -H "Content-Type: application/json" \
                    -H "Accept: application/json" \
                    -H "User-Agent: Flair Puck 1.0" \
                    -H "Authorization: Bearer $AUTH_TOKEN" \
                    -X POST \
                    -d '{
                        "puck_statuses": [{
                            "id": "'$PUCK_ID'",
                            "tem": 2200,
                            "pre": 10000,
                            "rss": -42,
                            "svo": 330,
                            "hum": 60,
                            "lig": 40,
                            "bpu": 0,
                            "dsi": 53886,
                            "rec": 0,
                            "fww": 85,
                            "dte": 2500,
                            "dsi": "'$((0x${DESIRED_STATE_ID}))'"

                       }],
                       "vent_statuses": []
                    }' \
                    "${API_ROOT}puck-api/sensor-readings?version=4" ;;

    "confirm_puck_ir_codes_download") curl \
                        -i \
                        -H "Content-Type: application/json" \
                        -H "Accept: text/plain" \
                        -H "User-Agent: Flair Puck 1.0" \
                        -H "Authorization: Bearer $AUTH_TOKEN" \
                        "${API_ROOT}puck-api/${PUCK_ID}/ir-codes" ;;

    *) echo "./puck-api.sh [get_access_token|post_puck_status|confirm_puck_ir_codes_download]" ;;
esac
