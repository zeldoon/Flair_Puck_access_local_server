from typing import Tuple

import pytest
from playwright.sync_api import APIRequestContext, Page, expect, Request, Route, Locator
from modules.constants import UiConstants
from modules.easy import HelpMethods
from modules.locators import Locators
from time import sleep
from mocks import sid_12 as home
import json


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["room_tile"]


def test_vent_identification_mode_toggle__QA_182(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    get_puck,
    constants: UiConstants,
    easy: HelpMethods,
    locators: Locators,
):
    (page, api) = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    FD_VI_MODE_CHECK = page.get_by_test_id("vent-identification-mode").get_by_role("checkbox")

    hc_mode = page.get_by_text("Change heat/cool mode?")
    try:
        hc_mode.wait_for(timeout=3000)
        page.get_by_role("button", name="Cancel").click()
    except:
        pass

    locators.navicon.click()
    locators.flair_menu_home_settings.click()
    page.get_by_text("Flair Devices").click()
    if not FD_VI_MODE_CHECK.is_checked():
        FD_VI_MODE_CHECK.click()
        easy.text_visible("Toggle to end Identification Mode")
        # TODO: report slow switch and reactivate test steps below
        # easy.text_visible('Enabling Setup Mode')
        # easy.text_visible("Setup Mode is on.")
        # expect(page.get_by_text('Please wait')).not_to_be_visible(timeout=20000)
    else:
        print("Vent ID Mode was already enabled! Please revise your tests or fixtures.")
    # easy.text_visible("Turn off to prevent")
    FD_VI_MODE_CHECK.click()


def test_flair_devices_preferences__QA_183(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    get_puck,
    constants: UiConstants,
    easy: HelpMethods,
    locators: Locators,
):
    (page, api) = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    FD_SHOW_ALERTS_CHECK = page.get_by_test_id("show-alerts").get_by_role("checkbox")
    hc_mode = page.get_by_text("Change heat/cool mode?")
    try:
        hc_mode.wait_for(timeout=3000)
        page.get_by_role("button", name="Cancel").click()
    except:
        pass

    locators.navicon.click()
    locators.flair_menu_home_settings.click()
    page.get_by_text("Flair Devices").click()
    for scale in ["Celsius", "Fahrenheit", "Kelvin"]:
        with page.expect_request(
            lambda rq: rq.method == "PATCH" and "structure" in rq.url
        ) as patch_info:
            page.get_by_test_id("testid-temp").click()
            page.get_by_role("menuitem").get_by_text(scale).click()
        patch_payload = patch_info.value.post_data_json
        assert "temperature-scale" in patch_payload["data"]["attributes"].keys()
        assert patch_payload["data"]["attributes"]["temperature-scale"] == scale[0]
        expect(page.get_by_test_id("testid-temp").get_by_text(scale)).to_be_visible()
    page.get_by_test_id("testid-temp").click()
    page.get_by_role("menuitem").get_by_text("Fahrenheit").click()
    expect(page.get_by_test_id("testid-temp").get_by_text("Fahrenheit")).to_be_visible()

    # SHOW ALERTS
    # TODO: Actually check if alerts stop happening
    page.get_by_test_id("show-alerts").click()
    expect(FD_SHOW_ALERTS_CHECK).not_to_be_checked()
    page.get_by_test_id("show-alerts").click()


def test_flair_devices_vent_view__QA_191(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    get_puck,
    get_vent_from_puck,
    standard_headers,
    connect_flair_devices,
    constants: UiConstants,
    easy: HelpMethods,
    locators: Locators,
):
    (page, api) = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    connect_flair_devices(home)

    hc_mode = page.get_by_text("Change heat/cool mode?")
    try:
        hc_mode.wait_for(timeout=3000)
        page.get_by_role("button", name="Cancel").click()
    except:
        pass

    locators.navicon.click()
    locators.flair_menu_home_settings.click()
    page.get_by_text("Flair Devices").click()
    vent_entry = page.get_by_test_id("vent-list").get_by_role("button")
    vent_entry.click()
    found_vent_thumb = False
    for img in page.get_by_role("img").all():
        if img.is_visible():
            if img.get_attribute("src") == "/img/vent.png":
                found_vent_thumb = True
                break
    assert found_vent_thumb

    def reopen_view(nameplate: Locator):
        downs = [
            loc
            for loc in page.locator("path").all()
            if loc.get_attribute("d") == constants.down_arrow_path and loc.is_visible()
        ]
        if len(downs) > 0:
            nameplate.click()

    for vent in home.vents.values():
        nameplate = page.get_by_text(f"{vent['id'][:4]} -")
        nameplate.click()
        # TODO: get room info and ensure that it's correct in name plate
        # we are closing our trays after running our tests; should only have one vent view open
        easy.any_text_visible(vent["id"])
        gateway_id = vent["attributes"]["connected-gateway-puck-id"]
        gateway_info = api.get(
            f"{api_url}/api/pucks/{gateway_id}", headers=standard_headers
        )
        puck_resp = gateway_info.json()
        gateway_name = puck_resp["data"]["attributes"]["name"]
        reopen_view(nameplate)
        easy.text_visible(f"Connected Gateway Puck: {gateway_name}")
        page.get_by_text("Remove Device From Home").click()
        circle_xs = [
            loc
            for loc in page.locator("path").all()
            if loc.get_attribute("d") == constants.circle_x_path and loc.is_visible()
        ]
        assert len(circle_xs) == 1
        active_lights = []
        for ul in page.locator("ul").all():
            try:
                ul.scroll_into_view_if_needed(timeout=2000)
            except:
                pass
            if ul.is_visible():
                active_lights.append(ul)
        assert len(active_lights) == 1
        lightcode = 0
        for i, li in enumerate(active_lights[0].locator("li").all()):
            bit = int(li.inner_text())
            lightcode += (2 ** (4 - i)) * bit
        assert lightcode == vent["attributes"]["setup-lightstrip"]
        assert (
            page.get_by_label("Vent Name").get_attribute("value")
            == vent["attributes"]["name"]
        )
        easy.any_text_visible("Assigned to Room")
        # TODO: File ticket on ID not always visible
        # easy.text_visible(f"ID: {vent['id']}")
        nameplate.click()
        expect(
            page.get_by_role("input").get_by_text(vent["attributes"]["name"])
        ).not_to_be_visible()
