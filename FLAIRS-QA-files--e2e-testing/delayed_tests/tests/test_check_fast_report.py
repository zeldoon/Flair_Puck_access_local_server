from typing import Tuple

import pytest

from playwright.sync_api import APIRequestContext, Page

REPORTING_INT_ENDPOINT = 'reporting-intervals'
INTERVALS = {
    'short': {
        'gateway': 64,
        'sensor': 72,
        'vent': 72
    },
    'long': {
        'gateway': 255,
        'sensor': 255,
        'vent': None
    }
}

@pytest.fixture()
def test_case(testenv):
    return testenv['case']['fast_report_expire']

def test_check_fast_report_period_expired(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], standard_headers
):
    (page, api) = page_and_api
    start_url = testenv['url'][testenv['env']]['site']
    api_url = testenv['url'][testenv['env']]['api']

    pucks_response = api.get(f'{api_url}/api/structures/{test_case["structure_id"]}/pucks', headers=standard_headers)
    pucks_json = pucks_response.json()

    for puck_id in [entry['attributes']['id'] for entry in pucks_json['data']]:
        puck_resp_info = api.get(f'{api_url}/api/pucks/{puck_id}/current-state', headers=standard_headers)
        puck_resp = puck_resp_info.json()
        puck_type = 'sensor'
        if 'is_gateway' in puck_resp['data']['attributes']:
            if puck_resp['data']['attributes']['is_gateway'] is True:
                puck_type = 'gateway'
        assert puck_resp['data']['attributes']['reporting-interval-ds'] == INTERVALS['long'][puck_type]

    vents_response = api.get(f'{api_url}/api/structures/{test_case["structure_id"]}/vents', headers=standard_headers)
    vents_json = vents_response.json()

    for vent_id in [entry['attributes']['id'] for entry in vents_json['data']]:
        vent_resp_info = api.get(f'{api_url}/api/vents/{vent_id}/current-state', headers=standard_headers)
        vent_resp = vent_resp_info.json()
        assert (
            'reporting-interval-ms' not in vent_resp['data']['attributes'].keys() or \
            vent_resp['data']['attributes']['reporting-interval-ms'] == INTERVALS['long']['vent']
        )