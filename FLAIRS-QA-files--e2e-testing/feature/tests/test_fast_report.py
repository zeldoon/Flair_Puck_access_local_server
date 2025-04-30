from typing import Tuple
from time import sleep
from datetime import datetime
from modules.easy import HelpMethods
import json

import pytest

from playwright.sync_api import (
    APIRequestContext,
    Page,
    Request,
    Route,
    expect,
    BrowserContext,
)

REPORTING_INT_ENDPOINT = "reporting-intervals"
INTERVALS = {
    "short": {"gateway": 64, "sensor": 72, "vent": 72},
    "long": {"gateway": 255, "sensor": 255, "vent": None},
}


# LOCATORS
class Locators:
    def __init__(self, page: Page):
        self.page = page
        self.unfinished_setup_dialog = page.get_by_test_id("unfinished-setup-dialog")
        self.unfinished_setup_close = page.get_by_test_id("unfinished-setup-close")
        self.nav_icon = page.get_by_test_id("nav-icon")
        self.nav_menu_sign_out = page.get_by_role("menuitem").get_by_text("Sign Out")
        self.sign_in = page.get_by_role("button").get_by_text("Sign In")


@pytest.fixture()
def locators(page_and_api: Tuple[Page, APIRequestContext]):
    return Locators(page_and_api[0])


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["fast_report"]


def route_rep_int(route: Route, request: Request):
    new_post_data = request.post_data_json | {"interval": 1}  # type: ignore
    route.continue_(post_data=new_post_data)


@pytest.fixture()
def preauth(page_and_api: Tuple[Page, APIRequestContext]):
    (page, _) = page_and_api
    try:
        page.context.tracing.stop_chunk()
    except:
        print("Tracing already stopped")
    page.route(f"**/{REPORTING_INT_ENDPOINT}", route_rep_int)

# @pytest.mark.skip()
def test_fast_report_on_login_and_reporting_intervals_as_expected_and_debounce(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], standard_headers
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    nonadmin_headers = standard_headers | {"X-Admin-Mode": "false"}

    pucks_response = api.get(
        f'{api_url}/api/structures/{test_case["structure_id"]}/pucks',
        headers=nonadmin_headers,
    )
    pucks_json = pucks_response.json()

    for puck in pucks_json["data"]:
        puck_id = puck["id"]
        puck_resp_info = api.get(
            f"{api_url}/api/pucks/{puck_id}/current-state", headers=standard_headers
        )
        puck_resp = puck_resp_info.json()
        puck_type = "sensor"
        if "is-gateway" in puck["attributes"]:
            if puck["attributes"]["is-gateway"] is True:
                puck_type = "gateway"
        assert (
            puck_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["short"][puck_type]
        )

    vents_response = api.get(
        f'{api_url}/api/structures/{test_case["structure_id"]}/vents',
        headers=nonadmin_headers,
    )
    vents_json = vents_response.json()

    for vent_id in [entry["id"] for entry in vents_json["data"]]:
        vent_resp_info = api.get(
            f"{api_url}/api/vents/{vent_id}/current-state", headers=nonadmin_headers
        )
        vent_resp = vent_resp_info.json()
        assert (
            vent_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["short"]["vent"]
        )

    passed = True

    def rq_sent(rq: Request):
        if rq.url.endswith(REPORTING_INT_ENDPOINT):
            global passed
            passed = False

    page.on("request", rq_sent)
    page.mouse.click(120, 120)
    sleep(3)  # hard wait to see if reporting-interval call bounces
    assert passed

    sleep(57)
    for puck in pucks_json["data"]:
        puck_id = puck["id"]
        puck_resp_info = api.get(
            f"{api_url}/api/pucks/{puck_id}/current-state", headers=standard_headers
        )
        puck_resp = puck_resp_info.json()
        puck_type = "sensor"
        if "is-gateway" in puck["attributes"]:
            if puck["attributes"]["is-gateway"] is True:
                puck_type = "gateway"
        assert (
            puck_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["long"][puck_type]
        )

    api.post(
        f"{api_url}/api/{REPORTING_INT_ENDPOINT}",
        data='{"fast_report": false}',
        headers=standard_headers,
    )
    try:
        page.context.tracing.start_chunk(screenshots=True, snapshots=True, sources=True)
    except:
        print("Tracing already underway")


# @pytest.mark.skip()
def test_fast_report_reverts_after_logout__QA_79(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    easy: HelpMethods,
    locators: Locators,
    standard_headers,
):
    (page, api) = page_and_api
    api_url = testenv["url"][testenv["env"]]["api"]

    if locators.unfinished_setup_dialog.count() > 0:
        locators.unfinished_setup_close.click()
    locators.nav_icon.click()

    with easy.wait_for_response("GET", ""):
        with easy.wait_for_request("POST", REPORTING_INT_ENDPOINT) as rep_int_req:
            locators.nav_menu_sign_out.click(delay=2000)
    rep_int_payload = rep_int_req.value.post_data_json
    assert rep_int_payload["fast_report"] is False  # type: ignore

    expect(locators.sign_in).to_be_visible(timeout=20000)

    pucks_response = api.get(
        f'{api_url}/api/structures/{test_case["structure_id"]}/pucks',
        headers=standard_headers,
    )
    pucks_json = pucks_response.json()

    for puck in pucks_json["data"]:
        puck_id = puck["id"]
        puck_resp_info = api.get(
            f"{api_url}/api/pucks/{puck_id}/current-state", headers=standard_headers
        )
        puck_resp = puck_resp_info.json()
        puck_type = "sensor"
        if "is-gateway" in puck["attributes"]:
            if puck["attributes"]["is-gateway"] is True:
                puck_type = "gateway"
        assert (
            puck_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["long"][puck_type]
        )

    vents_response = api.get(
        f'{api_url}/api/structures/{test_case["structure_id"]}/vents',
        headers=standard_headers,
    )
    vents_json = vents_response.json()

    for vent_id in [entry["id"] for entry in vents_json["data"]]:
        vent_resp_info = api.get(
            f"{api_url}/api/vents/{vent_id}/current-state", headers=standard_headers
        )
        vent_resp = vent_resp_info.json()
        assert (
            "reporting-interval-ds" not in vent_resp["data"]["attributes"].keys()
            or vent_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["long"]["vent"]
        )
    try:
        page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    except:
        print("Tracing already underway")
