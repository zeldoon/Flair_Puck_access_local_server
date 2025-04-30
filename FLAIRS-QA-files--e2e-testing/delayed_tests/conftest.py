from time import sleep
from typing import Tuple, Generator
from random import shuffle
from os import environ
import json, re

import pytest

from playwright.sync_api import APIRequestContext, BrowserContext, Page, Route, expect

def load_from_json(filename: str) -> dict:
    with open(filename) as fh:
        return json.load(fh)

@pytest.fixture()
def env() -> dict:
    """The env.json file relevant to the test type, parsed."""
    return load_from_json(f"feature/env.json")

@pytest.fixture()
def settings() -> dict:
    """The settings.json file relevant to the test type, parsed."""
    return load_from_json(f"feature/settings.json")

@pytest.fixture(autouse=True, scope="function")
def auth(page_and_api: Tuple[Page, APIRequestContext], testenv, test_case):
    """Authenticate via UI, yield (page, api) Tuple, then log out as teardown, removing token from localStorage."""
    (page, api) = page_and_api
    test_env = testenv['env']
    creds = test_case['auth']
    url = testenv['url'][test_env]['site']
    auth_success = False
    for _ in range(2):
        try:
            page.goto(url)
            if page.get_by_test_id('nav-icon').count() == 0:
                page.get_by_role('button').get_by_text("Sign In").click(timeout=15000)
                page.locator("[name=email]").fill(creds["username"])
                page.locator("[name=password]").fill(creds["password"])
                page.get_by_text('Remember me').uncheck()
                sleep(0.2) # short hard wait because sometimes we get race condition
                with page.expect_response(lambda rs: "authorize?code" in rs.url) as authorize:
                    page.locator("[type=submit]").click()
                assert authorize.value.ok
                expect(page.get_by_role('button').get_by_text('Sign in')).not_to_be_visible(timeout=30000)
            page.wait_for_load_state()
            expect(page.get_by_test_id('nav-icon').first).to_be_visible()
            auth_success = True
            break
        except:
            print('Failed to auth! Retrying...')
    assert auth_success
    yield True

@pytest.fixture()
def access_token(page_and_api: Tuple[Page, APIRequestContext], auth):
    """Given an auth fixture, what is the active access token?"""
    (page, _) = page_and_api
    api_tokens = [dct['value'] for dct in page.context.storage_state()['origins'][0]['localStorage'] if dct['name'] == 'api-tokens'][0] # type: ignore
    access_token_re = re.compile(r'access-token "(.*?)"')
    try:
        return access_token_re.search(api_tokens).group(1)
    except:
        return None

@pytest.fixture(autouse=True)
def testenv(env):
    if 'TEST_ENV' not in environ:
        return env | {'env': 'ft'}
    else:
        return env | {'env': environ['TEST_ENV']}