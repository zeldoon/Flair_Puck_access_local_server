from typing import Tuple

import pytest
from playwright.sync_api import APIRequestContext, Page, expect, Locator

from time import sleep
from modules.easy import HelpMethods
from modules.locators import Locators
from modules.constants import UiConstants


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["thermostat_settings"]
    # REUSING thermostat_settings as it's a fairly normal case we're unlikely to get test interference from


# @pytest.mark.skip()
def test_flair_menu_layout_normal_case__QA_138(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], locators: Locators, disable_setup_mode
):
    (page, _) = page_and_api

    start_url = testenv["url"][testenv["env"]]["site"]

    normal_user_owned_home_navbar = [
        (locators.flair_menu_home_settings, "/config/"),
        (locators.flair_menu_home_statistics, "/stats/"),
        (locators.flair_menu_get_support, locators.support_modal_title),
        (locators.flair_menu_notifications, "/../../notifications"),
        (locators.flair_menu_account_settings, "/../../account"),
        (locators.flair_menu_sign_out, locators.sign_in_button),
    ]

    admin_user_only = [
        locators.flair_menu_admin_mode,
        locators.flair_menu_home_logs,
        locators.flair_menu_home_manual,
        locators.flair_menu_occupancy_explanations,
    ]

    page.goto(start_url)
    locators.navicon.click()
    for locator in admin_user_only:
        expect(locator).not_to_be_visible()

    for locator, target in normal_user_owned_home_navbar:
        page.goto(start_url)
        locators.navicon.click()
        resolved_url = page.url
        target_url = resolved_url
        expect(locator).to_be_visible()
        locator.click()
        if type(target) == str:
            resolved_parts = resolved_url.split("/")
            target_parts = target.split("/")
            for target_part in target_parts[1:]:
                if target_part == "..":
                    resolved_parts.pop()
                else:
                    resolved_parts.append(target_part)
            target_url = "/".join(resolved_parts)
            page.wait_for_url(target_url, wait_until="commit")
        elif type(target) == Locator:
            expect(target).to_be_visible()


# @pytest.mark.skip()
def test_flair_menu_layout_unowned_home__QA_138(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], locators: Locators, disable_setup_mode
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
def test_structure_view_layout__QA_139(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    locators: Locators,
    easy: HelpMethods,
    constants: UiConstants,
    disable_setup_mode,
):
    (page, _) = page_and_api

    start_url = testenv["url"][testenv["env"]]["site"]

    structure_view_badges = {
        "home_away": locators.control_home_away,
        "weather": locators.control_weather,
        "set_point": locators.control_set_point,
        "system_mode": locators.control_system_mode,
        "heat_cool_mode": locators.control_heat_cool_mode,
        "schedule": locators.control_schedule,
    }

    page.goto(start_url)
    for badge_name, locator in structure_view_badges.items():
        expect(locator).to_be_visible()
        if locator == locators.control_weather:
            continue
        locator.click()
        easy.any_text_visible(constants.control_popover_text[badge_name])
        page.reload()


# @pytest.mark.skip()
def test_plus_menu_layout__QA_142(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    constants: UiConstants,
    easy: HelpMethods,
    standard_headers,
    disable_setup_mode,
):
    (page, api) = page_and_api

    # TODO: Set up Home with secondary heat

    start_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]
    setup_mode_off_payload = {
        "data": {"type": "structures", "attributes": {"setup-mode": False}}
    }

    page.goto(start_url)
    loading = page.get_by_text("Loading ...").all()
    [expect(loc).not_to_be_visible() for loc in loading]
    page.wait_for_load_state("domcontentloaded")

    for link, target in constants.standard_plus_menu_items:
        api.patch(
            f'{api_url}/api/structures/{test_case["structure_id"]}',
            headers=standard_headers,
            data=setup_mode_off_payload,
        )
        sleep(5)
        page.wait_for_load_state("domcontentloaded")
        done_setup = [
            loc
            for loc in page.get_by_text(constants.setup_mode_end).all()
            if loc.is_visible()
        ]
        if len(done_setup) > 0:
            done_setup[0].click()
            try:
                page.get_by_role("button", name="YES").click()
            except:
                pass
            page.reload()
        page.get_by_test_id("add-home-floating-plus").scroll_into_view_if_needed()
        page.get_by_test_id("add-home-floating-plus").click()
        easy.any_text_visible(link)
        page.get_by_role("button").filter(has_text=link).click()
        easy.any_text_visible(target)
        page.wait_for_load_state("domcontentloaded")
        cancel_x = [
            loc
            for loc in page.locator(f'svg > path[d="{constants.cancel_path}"]').all()
            if loc.is_visible()
        ]
        if len(cancel_x) > 0:
            cancel_x[0].click()
        page.wait_for_load_state("domcontentloaded")
        in_setup = [
            loc
            for loc in page.get_by_text(constants.setup_mode_active).all()
            if loc.is_visible()
        ]
        if len(in_setup) > 0:
            setup_off = api.patch(
                f'{api_url}/api/structures/{test_case["structure_id"]}',
                headers=standard_headers,
                data=setup_mode_off_payload,
            )
            assert setup_off.ok
            sleep(3)
        page.wait_for_load_state("domcontentloaded")
        page.goto(start_url)

    final_setup_patch = api.patch(
        f'{api_url}/api/structures/{test_case["structure_id"]}',
        headers=standard_headers,
        data=setup_mode_off_payload,
    )
    assert final_setup_patch.ok
