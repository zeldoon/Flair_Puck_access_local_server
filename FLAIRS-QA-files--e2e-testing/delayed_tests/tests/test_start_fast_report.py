from typing import Tuple
from time import sleep
from datetime import datetime

import pytest

from playwright.sync_api import APIRequestContext, Page

@pytest.fixture()
def test_case(testenv):
    return testenv['case']['fast_report_expire']

def test_null():
    pass

# leaving the following as an example of how to perform a delayed test
@pytest.mark.skip()
def test_set_fast_report_period(
    testenv, test_case, page_and_api: Tuple[Page, APIRequestContext], standard_headers
):
    (page, api) = page_and_api
    start_url = testenv['url'][testenv['env']]['site']
    api_url = testenv['url'][testenv['env']]['api']
    page.goto(start_url)

    sleep(2)
    page.mouse.click(120,120)
    with open('start_time', 'w') as fh:
        fh.write(datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%M:%S'))