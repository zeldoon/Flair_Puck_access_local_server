from time import sleep
from typing import Tuple, Generator
from random import shuffle
from os import environ
import re

import pytest

from playwright.sync_api import APIRequestContext, BrowserContext, Page, Route, expect

# CONFTEST.PY is a special file in PyTest that sets up needed fixtures, configures tests, and does session-
#  level setup and takedown.

@pytest.fixture(autouse=True, scope="function")
def preauth():
    pass

@pytest.fixture(autouse=True, scope="function")
def auth(page_and_api: Tuple[Page, APIRequestContext], testenv, test_case, preauth):
    """Authenticate via UI, yield (page, api) Tuple, then log out as teardown, removing token from localStorage."""
    (page, api) = page_and_api
    try:
        page.context.tracing.start_chunk()
    except:
        print("Tracing already active...")
    this_testenv = testenv['env']
    creds = test_case['auth']
    url = testenv['url'][this_testenv]['site']
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
    page.goto(url)
    page.wait_for_load_state()
    for loc in page.get_by_text('Loading ...').all():
        expect(loc).not_to_be_visible(timeout=15000)
    if page.get_by_test_id('unfinished-setup-close').is_visible():
        page.get_by_test_id('unfinished-setup-close').dispatch_event('click')
    if page.get_by_test_id('nav-icon').is_visible():
        page.get_by_test_id('nav-icon').dispatch_event('click')
    if page.get_by_test_id('navbar-sign-out').is_visible():
        page.get_by_test_id('navbar-sign-out').dispatch_event('click')
    else:
        page.evaluate('window.localStorage = ""')

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

@pytest.fixture()
def delete_homes(page_and_api: Tuple[Page, APIRequestContext], auth, testenv, test_case, access_token):
    """Method factory: given a list of SIDs, delete them all"""
    (page, api) = page_and_api
    def _delete_homes(sid_list: list):
        api_url = testenv['url'][testenv['env']]['api']
        headers = {
            "Authorization": f'Bearer {access_token}',
            "Content-Type": "application/json",
            "X-Admin-Mode": "admin",
        }
        for structure_id in sid_list:
            delete_url = f'{api_url}/api/structures/{structure_id}'
            delete_response_info = api.delete(delete_url, headers=headers)
            assert delete_response_info.ok
            print(f'Deleted home: SID {structure_id}')
    return _delete_homes


@pytest.fixture(scope='module')
def random_house_name():
    """Provide a random string of 5 characters, no repeats"""
    def _random_house_name():
        while True:
            i = 0
            abc = list('abcdefghijklmnopqrstuvwxyz')
            shuffle(abc)
            while i < 21:
                yield ''.join(abc[i:i+5])
                i += 5

    return _random_house_name

@pytest.fixture(autouse=True)
def testenv(env):
    if 'TEST_ENV' not in environ:
        return env | {'env': 'ft'}
    else:
        return env | {'env': environ['TEST_ENV']}
