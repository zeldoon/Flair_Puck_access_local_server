from typing import Tuple

import pytest
from playwright.sync_api import APIRequestContext, Page, expect

SENSOR_NAME = "Bedroom Sensor"


@pytest.fixture()
def test_case(
    testenv,
):
    return testenv["case"]["thermostat_settings"]


# @pytest.mark.skip()
def test_remote_sensors_in_thermostat_settings(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
):
    """
    A home with an unsupported thermostat (Lennox) that has 1 paired remote sensor in a different
    room. Remote Sensor should show up in Thermostat Settings.
    """
    page, api = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    # api_url = testenv['url'][testenv['env']]['api']
    structure_id = test_case["structure_id"]

    # navigate to home screen -> home settings -> thermostat settings
    page.goto(f"{base_url}/h/{structure_id}")
    page.get_by_test_id("nav-icon").click()
    page.locator("div").get_by_text("Home Settings").click()
    page.locator("div").get_by_text("Thermostats").click()

    # check for subsection
    expect(page.get_by_test_id("remote-sensors-subheader")).to_be_visible()

    # check collapsed Bedroom Sensor
    li = page.locator("div.MuiListItem-root").filter(has_text=SENSOR_NAME)
    expect(li).to_be_visible()
    expect(li.get_by_text(SENSOR_NAME)).to_be_visible()
    # expect(li.get_by_text('Lennox')).to_be_visible()
    expect(li.get_by_role("img")).to_be_visible()

    # expand room sensor
    chevron = li.locator("svg")
    chevron.click()
    expect(chevron).to_be_visible()

    # check sensor ID
    expect(page.locator("li").get_by_text("Remote Sensor ID")).to_be_visible()

    # check sensor name input
    expect(page.locator("div").get_by_text("Remote Sensor Name")).to_be_visible()
    page.locator("div").get_by_label("Remote Sensor Name").fill(SENSOR_NAME[::-1])
    assert (
        page.locator("div").get_by_label("Remote Sensor Name").input_value(timeout=6000)
        == SENSOR_NAME[::-1]
    )

    # check sensor location menu
    expect(page.locator("div").get_by_text("Remote Sensor Location")).to_be_visible()
    expect(page.locator("div").get_by_text("Bedroom", exact=True)).to_be_visible()
    location = page.locator("div").get_by_text("Remote Sensor Location")
    location.click()
    menu = page.get_by_role("menu")
    menu.get_by_text("Bedroom").click()
    expect(page.get_by_role("menu")).to_have_count(0)
    expect(page.locator("div").get_by_text("Bedroom", exact=True)).to_be_visible()

    # check sensor pairing dialog
    pairing = page.locator("div").get_by_text("Thermostat Pairing")
    expect(pairing).to_be_visible()
    pairing.click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_role("button").click()
    expect(page.get_by_role("dialog")).to_have_count(0)
