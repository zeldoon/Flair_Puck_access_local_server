from playwright.sync_api import Page, APIRequestContext, Locator, expect
from time import sleep

class HelpMethods:
    """Provides syntactic sugar for some more complicated Playwright calls"""
    def __init__(self, page:Page, api:APIRequestContext):
        self.page = page
        self.api = api

    def next(self):
        """Click the Next button wisely."""
        nexts = self.page.get_by_role("button", name="Next")
        if nexts.count() < 1:
            sleep(0.75)
            nexts = self.page.get_by_role("button", name="Next")
        nexts.first.click(timeout=25000)

    def text_visible(self, text: str, kwargs={}):
        """Same as expect(page.get_by_text).to_be_visible()

        Arguments
        ---------

        text : str
            the text you are looking for
        kwargs : dict
            any other args that work on .to_be_visible
        """
        return expect(self.page.get_by_text(text)).to_be_visible(**kwargs)

    def any_text_visible(self, text):
        """Return true if any element with the target text is visible, rather than the first."""
        return any(
            [self.page.get_by_text(text).nth(x).is_visible()
                for x in range(self.page.get_by_text(text).count())]
        )

    def any_locator_visible(self, locator: Locator):
        """Return true if any element matching given locator is visible, rather than the first."""
        return any(
            [locator.nth(x).is_visible() for x in range(locator.count())]
        )

    def wait_for_response(self, method: str, endpoint: str):
        """Same as page.expect_response() but with the matcher-lambda built in

        Arguments
        ---------

        method : str
            the HTTP method of the expected response's request
        endpoint : str
            the last part of the URL of the expected response's request
        """
        return self.page.expect_response(
            lambda rs: rs.request.method == method and rs.request.url.endswith(endpoint)
        )

    def wait_for_request(self, method: str, endpoint: str):
        """Same as page.expect_request() but with the matcher-lambda built in

        Arguments
        ---------

        method : str
            the HTTP method of the expected request
        endpoint : str
            the last part of the URL of the expected request
        """
        return self.page.expect_request(
            lambda rq: rq.method == method and rq.url.endswith(endpoint)
        )