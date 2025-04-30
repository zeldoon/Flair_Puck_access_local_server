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


def test_flair_devices_gateway_puck_view__QA_186(
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

    gpuck_entry = page.get_by_test_id("gateway-puck-list").get_by_role("button")
    gpuck_entry.click()
    found_puck_thumb = False
    for img in page.get_by_role("img").all():
        if img.is_visible():
            if img.get_attribute("src") == "/img/puck.png":
                found_puck_thumb = True
                break
    assert found_puck_thumb

    def reopen_view(nameplate: Locator):
        downs = [
            loc
            for loc in page.locator("path").all()
            if loc.get_attribute("d") == constants.down_arrow_path and loc.is_visible()
        ]
        if len(downs) > 0:
            nameplate.click()

    for puck in home.gateway_pucks.values():
        nameplate = page.get_by_test_id("gateway-puck-list").get_by_text(f"{puck['attributes']['name']}")
        nameplate.click()
        # TODO: get room info and ensure that it's correct in name plate
        # we are closing our trays after running our tests; should only have one puck view open
        easy.any_text_visible(puck["id"])
        reopen_view(nameplate)

        page.get_by_text("Remove Device From Home").click()
        circle_xs = [
            loc
            for loc in page.locator("path").all()
            if loc.get_attribute("d") == constants.circle_x_path and loc.is_visible()
        ]
        assert len(circle_xs) == 1
        assert (
            page.get_by_label("Puck Name").get_attribute("value")
            == puck["attributes"]["name"]
        )
        easy.any_text_visible("Assigned to Room")
        easy.text_visible(f'Display Code: {puck["attributes"]["display-number"]}')

        expect(
            page.get_by_test_id("testid-display-color").get_by_text(
                "Puck Background Color"
            )
        )
        page.get_by_test_id("testid-display-color").click()
        expect(page.get_by_role("menuitem").get_by_text("White")).to_be_visible()
        expect(page.get_by_role("menuitem").get_by_text("Black")).to_be_visible()
        page.get_by_role("menuitem").get_by_text("White").click()

        expect(
            page.get_by_test_id("puck-lock-view").get_by_text("Lock Puck")
        ).to_be_visible()
        expect(
            page.get_by_test_id("puck-lock-view").get_by_role("checkbox")
        ).to_be_visible()

        spll = page.get_by_text("Set Point Lower Limit")
        spul = page.get_by_text("Set Point Upper Limit")
        tempcal = page.get_by_text("Temperature Calibration")
        div_w_slider = page.locator("div").filter(has=page.get_by_role("slider"))

        splldiv = page.locator("div").filter(has=spll).and_(div_w_slider)
        spuldiv = page.locator("div").filter(has=spul).and_(div_w_slider)
        tempcaldiv = page.locator("div").filter(has=tempcal).and_(div_w_slider)

        expect(splldiv.get_by_text("50")).to_be_visible()
        expect(spuldiv.get_by_text("90")).to_be_visible()

        tempcal_slider = tempcaldiv.locator('span [role="slider"]')

        nameplate.click()
        expect(
            page.get_by_role("input").get_by_text(puck["attributes"]["name"])
        ).not_to_be_visible()


def test_flair_devices_sensor_puck_view__QA_187(
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

    spuck_entry = page.get_by_test_id("sensor-puck-list").get_by_role("button")
    spuck_entry.click()
    found_puck_thumb = False
    for img in page.get_by_role("img").all():
        if img.is_visible():
            if img.get_attribute("src") == "/img/puck.png":
                found_puck_thumb = True
                break
    assert found_puck_thumb

    def reopen_view(nameplate: Locator):
        downs = [
            loc
            for loc in page.locator("path").all()
            if loc.get_attribute("d") == constants.down_arrow_path and loc.is_visible()
        ]
        if len(downs) > 0:
            nameplate.click()

    for puck in home.sensor_pucks.values():
        nameplate = page.get_by_text(f"{puck['attributes']['name']}")
        nameplate.click()
        # TODO: get room info and ensure that it's correct in name plate
        # we are closing our trays after running our tests; should only have one puck view open
        easy.any_text_visible(puck["id"])
        gateway_id = puck["attributes"]["connected-gateway-puck-id"]
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

        assert (
            page.get_by_label("Puck Name").get_attribute("value")
            == puck["attributes"]["name"]
        )
        easy.any_text_visible("Assigned to Room")
        easy.text_visible(f'Display Code: {puck["attributes"]["display-number"]}')

        expect(
            page.get_by_test_id("testid-display-color").get_by_text(
                "Puck Background Color"
            )
        )
        page.get_by_test_id("testid-display-color").click()
        expect(page.get_by_role("menuitem").get_by_text("White")).to_be_visible()
        expect(page.get_by_role("menuitem").get_by_text("Black")).to_be_visible()
        page.get_by_role("menuitem").get_by_text("White").click()

        expect(
            page.get_by_test_id("puck-lock-view").get_by_text("Lock Puck")
        ).to_be_visible()
        expect(
            page.get_by_test_id("puck-lock-view").get_by_role("checkbox")
        ).to_be_visible()

        spll = page.get_by_text("Set Point Lower Limit")
        spul = page.get_by_text("Set Point Upper Limit")
        tempcal = page.get_by_text("Temperature Calibration")
        div_w_slider = page.locator("div").filter(has=page.get_by_role("slider"))

        splldiv = page.locator("div").filter(has=spll).and_(div_w_slider)
        spuldiv = page.locator("div").filter(has=spul).and_(div_w_slider)
        tempcaldiv = page.locator("div").filter(has=tempcal).and_(div_w_slider)

        expect(splldiv.get_by_text("50")).to_be_visible()
        expect(spuldiv.get_by_text("90")).to_be_visible()

        tempcal_slider = tempcaldiv.locator('span [role="slider"]')

        nameplate.click()
        expect(
            page.get_by_role("input").get_by_text(puck["attributes"]["name"])
        ).not_to_be_visible()
