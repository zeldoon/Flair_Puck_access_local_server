from time import sleep
import re

import pytest

from typing import Tuple
from playwright.sync_api import BrowserContext, Page, APIRequestContext, expect

# The auth fixture logs in, yields the Page and the APIRequestContext associated with it.
#  It then logs out as teardown.

@pytest.fixture(autouse=True)
def auth(page_and_api: Tuple[Page, APIRequestContext], env):
    """Authenticate via UI, yield (page, api) Tuple, then delete home and log out as teardown."""
    (page, api) = page_and_api
    page.goto(env["url"]["site"])
    page.get_by_text("Sign In").click()
    page.locator("[name=email]").fill(env["auth"]["username"])
    page.locator("[name=password]").fill(env["auth"]["password"])
    with page.expect_response(lambda rs: "authorize?code" in rs.url) as authorize:
        page.locator("[type=submit]").click()
    try:
        expect(page.get_by_text("Loading").first).to_be_visible(timeout=10000)
    except:
        print("Didn't see 'Loading' screen...")
    sleep(1.500)
    yield (page, api)
    page.get_by_test_id("nav-icon").click()
    sleep(0.250)
    dialog = page.get_by_role("heading", name="Are you sure?")
    if dialog.count() > 0:
        page.get_by_text("Exit Setup").first.click()
        page.get_by_test_id("nav-icon").click()
    pw_test_loc = page.locator(
        "[data-testid=structures-list-item]", has_text=env["demo"]["home"]["name"])
    while pw_test_loc.count() > 0:
        target = pw_test_loc.first.get_attribute("href")
        page.goto(env["url"]["site"] + target)
        page.get_by_test_id("nav-icon").click()
        page.get_by_text("Home Settings").click()
        page.get_by_text("Manage Home").click()
        page.get_by_text("Delete Home").click()
        page.get_by_text("Delete").click()
        pw_test_loc = page.locator(
            "[data-testid=structures-list-item]", has_text=env["demo"]["home"]["name"])

    page.get_by_text("Sign Out").click()

@pytest.fixture()
def access_token(auth):
    """Given an auth fixture, what is the active access token?"""
    (page, _) = auth
    api_tokens = page.evaluate("window.localStorage['api-tokens']")
    access_token_re = re.compile(r'access-token "(.*?)"')
    try:
        return access_token_re.search(api_tokens).group(1)
    except:
        return None
