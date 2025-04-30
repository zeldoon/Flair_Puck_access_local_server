from typing import Tuple

import pytest
from playwright.sync_api import APIRequestContext, Page, expect, Request, Route
from modules.constants import UiConstants
from modules.easy import HelpMethods
from time import sleep


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["room_tile"]

# @pytest.mark.skip()
def test_room_tile_full_layout__QA_140(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    get_puck,
    constants: UiConstants,
    easy: HelpMethods,
):
    (page, api) = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]
    active_pucks = {}

    with page.expect_response(
        f'**/api/structures/{test_case["structure_id"]}/pucks'
    ) as puck_resp:
        page.goto(f'{base_url}/h/{test_case["structure_id"]}')
    for puck in puck_resp.value.json()["data"]:
        if puck["id"] not in active_pucks.keys():
            active_pucks[puck["id"]] = get_puck(
                api_url=api_url,
                sid=str(test_case["structure_id"]),
                env_name=testenv["env"],
                is_gateway=puck["attributes"]["name"] == "Gateway Puck",
                puck_id=puck["id"],
            )
            active_pucks[puck["id"]].get_access_token()
            active_pucks[puck["id"]].post_puck_status()
    sleep(2) # appears to matter for home staying in COOL
    page.reload()
    page.expect_response(
        f'**/api/structures/{test_case["structure_id"]}/pucks', timeout=30000
    )
    hc_mode = page.get_by_text("Change heat/cool mode?")
    try:
        hc_mode.wait_for(timeout=3000)
        page.get_by_role("button", name="Cancel").click()
    except:
        pass
    # TODO: get rooms from api
    for roomname in ["Den", "Bedroom"]:
        expect(page.locator("h3").get_by_text(roomname)).to_be_visible()
    found_blue_path = False
    for path_locator in page.locator("div", has_text="Den").locator("path").all():
        stroke_color = path_locator.get_attribute("stroke")
        if path_locator.is_visible() and stroke_color and stroke_color == "#1ac6ff":
            found_blue_path = True
    assert found_blue_path
    easy.any_locator_visible(
        page.locator("div", has_text="Den")
        .locator("svg")
        .locator("text")
        .get_by_text("72", exact=True)
    )

    page.get_by_text("Den").first.click()
    found_blue_path = False
    for path_locator in page.get_by_text("Den").locator("path").all():
        expect(path_locator).to_be_visible()
        stroke_color = path_locator.get_attribute("stroke")
        if stroke_color and stroke_color.lower() == "#1ac6ff":
            found_blue_path = True
    snowflakes = [
        loc
        for loc in page.locator("path").all()
        if loc.get_attribute("d") == constants.snowflake_path and loc.is_visible()
    ]
    assert len(snowflakes) == 1
    easy.any_text_visible("Temp")
    easy.any_text_visible("Humidity")
    active_toggle = page.get_by_role("checkbox")
    if not active_toggle.is_checked():
        active_toggle.click()
        confirm_home = page.get_by_role("button", name="Yes")
        try:
            confirm_home.wait_for(timeout=3000)
            confirm_home.nth(0).click()
        except:
            pass
    expect(page.get_by_role("checkbox")).to_be_checked()
    for device_type in ["Thermostats", "Gateway Pucks", "Vents"]:
        expect(page.get_by_role("listitem").get_by_text(device_type)).to_be_visible()
    easy.text_visible("Bob's Generic Thermostat")
    easy.text_visible("Gateway Puck is online")
    easy.text_visible("Vent in Den is offline")
    handle = None
    for loc in page.locator("circle").all():
        if loc.is_visible():
            assert loc.get_attribute("fill").lower() == "#16acde"
            if loc.get_attribute("r") == "10":
                handle = loc
    assert handle is not None
    toolbar = page.locator("div.replace-toolbar")
    # drag/drop test became flaky spontaneously--will investigate
    # see playwright docs on Locator.drag_to -- dragging "toward" the top left of toolbar
    # handle.drag_to(toolbar, target_position={"x": 100, "y": 145}, force=True)
    # easy.text_visible("Holding until", {"timeout": 20000})
    # easy.text_visible("64")
    # easy.text_visible("Holding until cleared")
    page.get_by_role("link").locator(f"svg > path").click()
    page.get_by_role("link", name="Bedroom").click()
    for device_type in ["Remote Sensors", "Sensor Pucks"]:
        expect(page.get_by_role("listitem").get_by_text(device_type)).to_be_visible()


# @pytest.mark.skip()
def test_remote_sensors_in_room_tile(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], get_puck
):
    """
    A home with an unsupported thermostat (Lennox) that has 1 paired remote sensor in a different
    room.
    """
    page, api = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]
    structure_id = test_case["structure_id"]

    # test room with Thermostat -- Den
    page.goto(f"{base_url}/h/{structure_id}")
    try:
        expect(page.get_by_text("Change heat/cool mode?")).to_be_visible(timeout=8000)
        page.get_by_role("button", name="Cancel").click()
    except:
        pass
    page.locator("h3").get_by_text("Den").click()
    expect(page.locator("li").get_by_text("Thermostats")).to_be_visible()
    expect(page.locator("li").get_by_text("Bob's Generic Thermostat")).to_be_visible()
    assert (
        page.locator("li").get_by_role("img", name="Unsupported").get_attribute("src")
        == "/img/generic-thermostat.png"
    )

    # test room with Remote Sensor -- Bedroom
    page.goto(f"{base_url}/h/{structure_id}")
    page.locator("h3").get_by_text("Bedroom").click()
    expect(page.locator("li").get_by_text("Remote Sensors")).to_be_visible()
    expect(page.locator("div").get_by_text("Bedroom Sensor")).to_be_visible()
    assert (
        page.get_by_role(
            "button",
            name="Bedroom Sensor Paired to thermostat: Bob's Generic Thermostat",
        )
        .locator("img")
        .get_attribute("src")
        == "/img/generic-thermostat.png"
    )
    expect(
        page.locator("div").get_by_text(
            "Paired to thermostat: Bob's Generic Thermostat"
        )
    ).to_be_visible()
