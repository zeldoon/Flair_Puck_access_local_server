from typing import Tuple

import pytest
from playwright.sync_api import APIRequestContext, Page, expect, Locator
from modules.easy import HelpMethods
from modules.locators import Locators
from modules.constants import UiConstants


@pytest.fixture()
def test_case(testenv):
    return testenv["case"]["user_tests"]


# @pytest.mark.skip()
def test_account_settings_layout__QA_145(
    testenv,
    test_case,
    page_and_api: Tuple[Page, APIRequestContext],
    easy: HelpMethods,
    locators: Locators,
    constants: UiConstants,
):
    (page, api) = page_and_api

    start_url = testenv["url"][testenv["env"]]["site"]
    page.goto(start_url)

    locators.navicon.click()
    locators.flair_menu_account_settings.click()
    expect(page.get_by_role("listitem").get_by_text("Account Settings")).to_be_visible()
    full_user_field = lambda name_type: page.locator(
        f'input[value="{test_case["user_"+name_type+"_name"]}"]'
    )
    empty_user_field = (
        lambda name_type: page.get_by_role("listitem")
        .filter(has_text=f"{name_type.title()} Name")
        .get_by_role("textbox")
    )
    for item in ['first', 'last']:
        expect(full_user_field(item)).to_be_visible()
        full_user_field(item).clear()

        with page.expect_request(
            lambda rq: rq.method == "PATCH"
            and rq.url.endswith(f"users/{test_case['user_id']}")
        ) as patch_user_info:
            empty_user_field(item).fill("Bill")

        patch_payload = patch_user_info.value.post_data_json
        mod_item = "" if item == 'first' else 'last-'
        assert patch_payload["data"]["attributes"][f"{mod_item}name"] == "Bill"

    full_email_field = page.locator(f'input[value="{test_case["user_email"]}"]')
    empty_email_field = page.locator('input[type="email"]')
    expect(full_email_field).to_be_visible()
    full_email_field.clear()

    with page.expect_request(
        lambda rq: rq.method == "PATCH"
        and rq.url.endswith(f"users/{test_case['user_id']}")
    ) as patch_user_info:
        empty_email_field.fill("bizarro@flair.co")

    patch_payload = patch_user_info.value.post_data_json
    assert patch_payload["data"]["attributes"]["email"] == "bizarro@flair.co"

    expect(
        page.get_by_test_id("user-bridge-setup").get_by_role("checkbox")
    ).not_to_be_enabled()
    with page.expect_request(
        lambda rq: rq.method == "PATCH"
        and rq.url.endswith(f"users/{test_case['user_id']}")
    ) as patch_user_info:
        page.get_by_test_id("user-is-partner").get_by_role("checkbox").click()

    patch_payload = patch_user_info.value.post_data_json
    assert patch_payload["data"]["attributes"]["partner"] == True
    expect(
        page.get_by_test_id("user-bridge-setup").get_by_role("checkbox")
    ).to_be_enabled()
    # TODO: When TECH-6330 addressed, change to check that
    # Bridge Setup Mode is deselected when partner deselected
    page.get_by_test_id("user-bridge-setup").get_by_role("checkbox").click()
    page.get_by_test_id("user-is-partner").get_by_role("checkbox").click(force=True)

    easy.text_visible("Change Password")
    page.get_by_test_id("user-submit-password").scroll_into_view_if_needed()
    page.get_by_test_id("user-change-password").get_by_role("textbox").fill("hamster")
    page.get_by_test_id("user-confirm-password").get_by_role("textbox").fill("gopher")
    easy.text_visible("Passwords do not match.")
    page.get_by_test_id("user-confirm-password").get_by_role("textbox").fill("hamster")
    with page.expect_request(
        lambda rq: rq.method == "PATCH"
        and rq.url.endswith(f"users/{test_case['user_id']}")
    ) as patch_user_info:
        page.get_by_test_id("user-submit-password").click()

    patch_payload = patch_user_info.value.post_data_json
    assert patch_payload["data"]["attributes"]["password"] == "hamster"

    for scale in ["Celsius", "Fahrenheit", "Kelvin"]:
        page.get_by_text("App Temperature Scale").click()
        with page.expect_request(
            lambda rq: rq.method == "PATCH"
            and rq.url.endswith(f"users/{test_case['user_id']}")
        ) as patch_user_info:
            page.get_by_role("menuitem", name=scale).click()

        patch_payload = patch_user_info.value.post_data_json
        assert patch_payload["data"]["attributes"]["temperature-scale"] == scale[0]

    page.get_by_text("App Temperature Scale").click()
    page.get_by_role("menuitem", name="Fahrenheit").click()

    noti_reasons = [
        "System Health",
        "Smart Away Temperature Exceeded",
        "Firmware Updates",
        "Energy Sense Events",
    ]
    for noti_type in ["Email", "Push Notification"]:
        page.wait_for_load_state("domcontentloaded")
        noti_short = noti_type.split(" ")[0]
        list_head = page.locator("ul", has_text=f"{noti_short} Settings")
        for reason in noti_reasons:
            list_head.get_by_role("listitem").filter(has_text=reason).get_by_role(
                "checkbox"
            ).scroll_into_view_if_needed()
            expect(
                list_head.get_by_role("listitem")
                .filter(has_text=reason)
                .get_by_role("checkbox")
            ).not_to_be_enabled()
        enable_notis = (
            list_head.get_by_role("listitem")
            .filter(has_text=f"Receive Flair Alerts by {noti_type}")
            .get_by_role("checkbox")
        )
        page.wait_for_load_state("domcontentloaded")
        expect(enable_notis).not_to_be_checked()
        enable_notis.click()
        for reason in noti_reasons:
            expect(
                list_head.get_by_role("listitem")
                .filter(has_text=reason)
                .get_by_role("checkbox")
            ).to_be_enabled()
        page.wait_for_load_state("domcontentloaded")
        enable_notis.click()
        expect(enable_notis).not_to_be_checked()

    page.get_by_text("Primary Home").click()
    expect(
        page.get_by_role("menuitem").get_by_text(test_case["primary_home_name"])
    ).to_be_visible()

    with page.expect_request(
        lambda rq: rq.method == "PATCH"
        and rq.url.endswith(f"users/{test_case['user_id']}")
    ) as patch_user_info:
        page.get_by_role("menuitem").get_by_text(
            test_case["secondary_home_name"]
        ).click()

    patch_payload = patch_user_info.value.post_data_json
    assert patch_payload["data"]["relationships"]["default-structure"]["data"][
        "id"
    ] == str(test_case["secondary_home_sid"])

    easy.any_text_visible(constants.delete_user_subheader)
    page.get_by_text("Delete Account").click()
    expect(page.get_by_test_id("delete-account-dialog")).to_be_visible()
    easy.any_text_visible(constants.delete_user_title)
    easy.any_text_visible(constants.delete_user_para_1_text)
    easy.any_text_visible(constants.delete_user_bold_text)
    page.get_by_role("button", name="Keep My Account").click()
    expect(page.get_by_test_id("delete-account-dialog")).not_to_be_visible()
    page.get_by_text("Delete Account").click()

    with page.expect_request(
        lambda rq: rq.method == "DELETE"
        and rq.url.endswith(f"users/{test_case['user_id']}")
    ) as patch_user_info:
        page.get_by_role("button", name="Delete My Account").click()

    page.evaluate('window.localStorage = ""')
    page.goto(start_url)
    page.wait_for_load_state("networkidle")
