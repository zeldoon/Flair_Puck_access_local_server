from typing import Tuple
from time import sleep
from modules.locators import Locators
from modules.easy import HelpMethods

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


@pytest.fixture()
def fast_report_tc(testenv):
    return testenv["case"]["fast_report"]


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["admin_user"]


# @pytest.mark.skip()
def test_flair_menu_layout_admin_normal__QA_138(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], locators: Locators
):
    (page, _) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]

    page.goto(start_url)
    locators.navicon.click()

    all_flair_menu = [
        locators.flair_menu_home_settings,
        locators.flair_menu_home_statistics,
        locators.flair_menu_admin_mode,
        locators.flair_menu_home_logs,
        locators.flair_menu_home_manual,
        locators.flair_menu_occupancy_explanations,
        locators.flair_menu_get_support,
        locators.flair_menu_notifications,
        locators.flair_menu_account_settings,
        locators.flair_menu_sign_out,
    ]

    for locator in all_flair_menu:
        expect(locator).to_be_visible()


# @pytest.mark.skip()
def test_flair_menu_layout_unowned_home__QA_138(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], locators: Locators
):
    (page, _) = page_and_api

    start_url = testenv["url"][testenv["env"]]["site"] + "/h/1"

    owned_home_and_admin = [
        locators.flair_menu_home_settings,
        locators.flair_menu_home_statistics,
        locators.flair_menu_admin_mode,
        locators.flair_menu_home_logs,
        locators.flair_menu_home_manual,
        locators.flair_menu_occupancy_explanations,
    ]

    unowned_home = [
        locators.flair_menu_get_support,
        locators.flair_menu_notifications,
        locators.flair_menu_account_settings,
        locators.flair_menu_sign_out,
    ]

    page.goto(start_url)
    locators.navicon.click()
    for locator in owned_home_and_admin:
        expect(locator).not_to_be_visible()

    for locator in unowned_home:
        expect(locator).to_be_visible()


# @pytest.mark.skip()
def test_reporting_interval_not_changed_for_admin__QA_77(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    standard_headers,
    fast_report_tc,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]
    page.goto(start_url)
    page.get_by_test_id("nav-icon").click()
    page.get_by_text("Admin Mode").click()  # TODO: add test-id in ui repo
    page.goto(f'{start_url}/h/{fast_report_tc["structure_id"]}')
    api.post(
        f"{api_url}/api/{REPORTING_INT_ENDPOINT}",
        data='{"fast_report":false}',
        headers=standard_headers,
    )
    page.mouse.click(120, 120)
    sleep(5)  # hard wait to see if reporting-interval call will happen

    pucks_response = api.get(
        f'{api_url}/api/structures/{test_case["structure_id"]}/pucks',
        headers=standard_headers,
    )
    pucks_json = pucks_response.json()

    for puck_id in [entry["attributes"]["id"] for entry in pucks_json["data"]]:
        puck_resp_info = api.get(
            f"{api_url}/api/pucks/{puck_id}/current-state", headers=standard_headers
        )
        puck_resp = puck_resp_info.json()
        puck_type = "sensor"
        if "is_gateway" in puck_resp["data"]["attributes"]:
            if puck_resp["data"]["attributes"]["is_gateway"] is True:
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

    for vent_id in [entry["attributes"]["id"] for entry in vents_json["data"]]:
        vent_resp_info = api.get(
            f"{api_url}/api/vents/{vent_id}/current-state", headers=standard_headers
        )
        vent_resp = vent_resp_info.json()
        assert (
            "reporting-interval-ds" not in vent_resp["data"]["attributes"].keys()
            or vent_resp["data"]["attributes"]["reporting-interval-ds"]
            == INTERVALS["long"]["vent"]
        )
