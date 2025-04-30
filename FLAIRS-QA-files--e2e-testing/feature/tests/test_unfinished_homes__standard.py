from typing import Callable, Tuple, Generator
from time import sleep
from datetime import datetime

import re

import pytest

from playwright.sync_api import (
    APIRequestContext,
    Page,
    Request,
    Route,
    expect,
    BrowserContext,
)
from modules.easy import HelpMethods
from modules.locators import Locators


@pytest.fixture()
def test_case(
    testenv,
):
    return testenv["case"]["unfinished_home_standard"]


# TECH-5921 - Incomplete Structure Flow Update

# SELECTORS

# SVG Paths for Icons
CHECKMARK_PATH = "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
WRENCH_PATH = "M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"

# V2A INCOMPLETE STRUCTURE DIALOG
V2A_INCOMPLETE_MSG = "You have not completed initial setup of <HOME>."
V2A_HOME_ID = "Home ID"
V2A_DEVICES = "Flair Devices"
V2A_ADDRESS = "Address"
V2A_CTIME = "Last Updated"
V2A_CONFIRM = "How would you like to proceed?"
V2A_TIME_FORMAT = "%A, %B %-d, %Y %-I:%M %p"

# V2B INCOMPLETE STRUCTURE DIALOG
V2B_INCOMPLETE_MSG = (
    "It looks like you were recently working on but did not complete setup of"
)

# DELETE HOME DIALOG
DELETE_HOME_TITLE = "Are You Sure?"
DELETE_HOME_GRAF_ONE = "Deleting <HOME> will not remove the 0 Flair vents and 1 Flair pucks from the home. You will need to manually remove them before you can add them to a new home."
DELETE_HOME_GRAF_TWO = "Don’t worry if there are minor issues with setup so far, you can easily fix them after setup is complete!"
DELETE_HOME_CONFIRM = "Are you sure you want to abandon setup and delete <HOME>?"
KB_LINK_TEXT = "Learn More"
KB_ARTICLE_RESET_DEVICES_URL = (
    "https://support.flair.co/hc/en-us/articles/12356472445709"
)

# OTHER NAV
SETUP_PLUG_IN_PUCK = "Plug in your Puck"
SETUP_WHAT_TO_CONTROL = "What do you want Flair to control?"


# HELPERS
def wait_for_unfinished_setup_dialog(page: Page):
    expect(page.get_by_test_id("unfinished-setup-dialog")).to_be_visible(timeout=15000)


# @pytest.mark.skip()
def test_tombstoned_homes_not_displayed_and_delete_dialog__QA_25_QA_31(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    random_house_name,
    build_to_puck_connect,
    locators: Locators,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    page.goto(start_url)
    house_name = next(random_house_name())
    if locators.unfinished_setup_close.count() > 0:
        locators.unfinished_setup_close.click()
    build_to_puck_connect(page, testenv["env"], start_url, api_url, house_name)

    page.goto(start_url)
    page.get_by_role("button").get_by_text("Delete Home").click()

    # QA-31 delete dialog nav
    expect(page.locator("h2").get_by_text(DELETE_HOME_TITLE)).to_be_visible()
    expect(
        page.get_by_text(DELETE_HOME_GRAF_ONE.replace("<HOME>", house_name))
    ).to_be_visible()
    assert (
        page.get_by_text(KB_LINK_TEXT).get_attribute("href")
        == KB_ARTICLE_RESET_DEVICES_URL
    )
    expect(page.get_by_text(DELETE_HOME_GRAF_TWO)).to_be_visible()
    expect(
        page.get_by_text(DELETE_HOME_CONFIRM.replace("<HOME>", house_name))
    ).to_be_visible()
    page.get_by_role("button").get_by_text("Cancel").click()

    page.goto(start_url)
    page.locator(locators.unfinished_setup_dialog)
    expect(locators.unfinished_setup_dialog).to_be_visible()
    page.get_by_role("button").get_by_text("Delete Home").click()
    page.get_by_role("button").get_by_text("delete").click()
    sleep(0.5)

    # QA-25 tombstoned homes do not appear
    page.goto(start_url)
    try:
        page.locator(locators.unfinished_setup_dialog, timeout=5000)
    except:
        pass
    if locators.unfinished_setup_dialog.count():
        if page.get_by_text(house_name).count():
            expect(page.get_by_text(house_name)).not_to_be_visible()
        locators.unfinished_setup_close.click()

    expect(locators.homes_menu_title).to_be_visible()
    locators.homes_menu_title.dispatch_event("click")
    caught = page.get_by_text(house_name)
    assert caught.count() == 0


# @pytest.mark.skip()
def test_homes_menu_icons_displayed_per_spec__QA_26(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    random_house_name,
    build_to_address,
    locators: Locators,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    # partial setup then test
    page.goto(start_url)
    house_name_one = next(random_house_name())
    build_to_address(page, start_url, house_name_one)
    page.goto(start_url)
    expect(locators.unfinished_setup_dialog).to_be_visible()
    locators.unfinished_setup_close.click()

    house_name_two = next(random_house_name())
    build_to_address(page, start_url, house_name_two)
    page.goto(start_url)

    expect(locators.unfinished_setup_dialog).to_be_visible()
    locators.unfinished_setup_close.click()

    locators.homes_menu_title.click()
    expect(locators.homes_menu).to_be_visible()
    list_items = page.locator("ul > a")
    for i in range(list_items.count()):
        anchor_text = list_items.nth(i).inner_text()
        if "test_home" in anchor_text:
            link_text = list_items.nth(i).get_attribute("href")
            sid = link_text.split("/")[-1]
            assert f"test_home - {sid}"
            if sid == "6":
                assert (
                    list_items.nth(i).locator("path").get_attribute("d")
                    == CHECKMARK_PATH
                )
            else:
                assert list_items.nth(i).locator("svg").is_hidden()
        elif "incomplete" in anchor_text:
            assert locators.incomplete_structure.count() > 1
            assert list_items.nth(i).locator("path").get_attribute("d") == WRENCH_PATH


# @pytest.mark.skip()
def test_homes_displayed_in_alphanum_order_in_homes_menu__QA_28(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    build_to_address,
    delete_homes,
    locators: Locators,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    to_delete = []
    homes = ["125 Miner", "300 Clay", "abacus", "apple", "Baseball"]
    for home in sorted(homes, reverse=True):
        sid = build_to_address(page, start_url, home)
        to_delete.append(sid)

    page.goto(start_url)
    locators.unfinished_setup_close.click()
    locators.homes_menu_title.click()
    expect(locators.incomplete_structure.first).to_be_visible()
    incompletes = locators.incomplete_structure
    # print(f'inc count {incompletes.count()}')
    found = -1
    for i in range(incompletes.count()):
        # print(incompletes.nth(i).inner_text())
        if found == len(homes) - 1:
            break
        this_home = incompletes.nth(i).inner_text()
        if this_home == homes[found + 1] or this_home.startswith(
            f"{homes[found+1]} - "
        ):
            found += 1

    assert found == len(homes) - 1
    delete_homes(to_delete)


# @pytest.mark.skip()
def test_transition_from_homes_menu_to_incomplete_setup_dialog__QA_29(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    build_to_address,
    locators: Locators,
    easy: HelpMethods,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    home = "QA_29"
    build_to_address(page, start_url, home)
    sid = page.url.split("/")[-2]
    timestamp = datetime.now()

    page.goto(start_url)
    with easy.wait_for_response("GET", "incomplete-setup-structures") as inc_rs:
        inc_response_obj = inc_rs.value.json()
    attrs = inc_response_obj["data"][0]["attributes"]
    street_city_state = f"{attrs['location']}, {attrs['city']}, {attrs['state']}"

    expect(locators.unfinished_setup_dialog).to_be_visible()
    locators.unfinished_setup_close.click()

    locators.homes_menu_title.click()
    if page.get_by_text(home).count() == 1:
        page.get_by_text(home).first.click()
    else:
        page.get_by_text(f"{home} - {sid}").first.click()

    expect(page.locator("h2").get_by_text(home)).to_be_visible()
    for element in [
        V2A_INCOMPLETE_MSG.replace("<HOME>", home),
        V2A_HOME_ID,
        V2A_DEVICES,
        V2A_ADDRESS,
        V2A_CTIME,
        V2A_CONFIRM,
    ]:
        expect(
            locators.unfinished_setup_dialog.get_by_text(element, exact=True)
        ).to_be_visible()
    expect(
        locators.unfinished_setup_dialog.page.get_by_text(sid, exact=True)
    ).to_be_visible()
    # TODO: add test ids and actually check values in the fields
    rendered_date = timestamp.strftime(V2A_TIME_FORMAT)
    expect(page.get_by_text(rendered_date)).to_be_visible()
    expect(page.get_by_text(street_city_state)).to_be_visible()


# @pytest.mark.skip()
def test_v2a_incomplete_setup_dialog_navigation__QA_30(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    build_to_address,
    build_to_puck_connect,
    locators: Locators,
    easy: HelpMethods,
    standard_headers,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    def select_home_from_menu(home: str) -> None:
        expect(locators.unfinished_setup_dialog).to_be_visible()
        locators.unfinished_setup_close.click()
        locators.homes_menu_title.click()
        locators.incomplete_structure.get_by_text(home).first.click()

    short_home = "short_home"
    long_home = "long_home"
    build_to_address(page, start_url, short_home)
    btpo = build_to_puck_connect(page, testenv["env"], start_url, api_url, long_home)

    page.goto(start_url)
    select_home_from_menu(short_home)
    expect(locators.unfinished_setup_dialog).to_be_visible()
    page.get_by_role("button", name="Resume Setup").click()
    expect(page.get_by_text(SETUP_PLUG_IN_PUCK)).to_be_visible()

    page.goto(start_url)
    expect(locators.unfinished_setup_dialog).to_be_visible()
    locators.unfinished_setup_close.click()
    locators.homes_menu_title.click()
    short_homes_count = locators.incomplete_structure.get_by_text(short_home).count()

    page.goto(start_url)
    select_home_from_menu(short_home)
    expect(locators.unfinished_setup_dialog).to_be_visible()
    with page.expect_response(
        lambda rs: rs.request.method == "DELETE" and "structures" in rs.request.url
    ) as del_call:
        page.get_by_role("button", name="Delete Home").click()
    assert del_call.is_done
    assert del_call.value.ok
    expect(page.get_by_text(f"Deleted {short_home}")).to_be_visible()
    expect(page.get_by_text(f"Deleted {short_home}")).not_to_be_visible()
    expect(page.get_by_text("Loading")).not_to_be_visible()
    page.goto(start_url)
    expect(page.get_by_text("Loading")).not_to_be_visible()

    for _ in range(10):
        if locators.unfinished_setup_dialog.is_visible():
            locators.unfinished_setup_close.click()
        sleep(0.5)  # bargain bin expect without a failure
    locators.homes_menu_title.click()
    assert (
        locators.incomplete_structure.get_by_text(short_home).count()
        == short_homes_count - 1
    )

    page.goto(start_url)
    select_home_from_menu(long_home)
    expect(page.get_by_test_id("unfinished-setup-dialog")).to_be_visible()
    page.get_by_role("button", name="Resume Setup").click()
    flair_control_text = page.get_by_text(SETUP_WHAT_TO_CONTROL)
    plug_in_puck_text = page.get_by_text(SETUP_PLUG_IN_PUCK)
    easy.any_locator_visible(flair_control_text.or_(plug_in_puck_text))

    page.goto(start_url)
    select_home_from_menu(long_home)
    page.get_by_role("button", name="Delete Home").click()
    expect(page.locator("h2").get_by_text(DELETE_HOME_TITLE)).to_be_visible()
    page.get_by_role("button", name="delete").click()


# @pytest.mark.skip()
def test_unfinished_setup_dialog_appearance_and_behavior__QA_32(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    random_house_name,
    build_to_address,
    delete_homes,
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]

    # We want random home names to avoid collision with other ephemeral fixtures.
    house_name_one = next(random_house_name())
    sid1 = build_to_address(page, start_url, house_name_one)

    # Case 3
    page.goto(start_url)
    wait_for_unfinished_setup_dialog(page)
    expect(page.get_by_text(f"{V2B_INCOMPLETE_MSG} {house_name_one}")).to_be_visible()

    house_name_two = next(random_house_name())
    sid2 = build_to_address(page, start_url, house_name_two)

    # Case 2
    page.goto(start_url)
    wait_for_unfinished_setup_dialog(page)
    expect(page.get_by_text(f"{V2B_INCOMPLETE_MSG} {house_name_two}")).to_be_visible()
    delete_homes([sid1, sid2])


# @pytest.mark.skip()
def test_unfinished_setup_dialog_not_appear_on_expired_setups__QA_32_Case_4(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], locators: Locators
):
    (page, api) = page_and_api
    start_url = testenv["url"][testenv["env"]]["site"]

    # testing current state
    page.goto(start_url)
    delete_home = page.get_by_role("button").get_by_text("Delete Home")
    while delete_home.count() > 0:
        delete_home.first.click()
        confirm = page.get_by_role("button").get_by_text("delete")
        if confirm.count() > 0:
            confirm.first.click()
        page.goto(start_url)
        delete_home = page.get_by_role("button").get_by_text("Delete Home")

    expect(locators.unfinished_setup_dialog).not_to_be_visible()
