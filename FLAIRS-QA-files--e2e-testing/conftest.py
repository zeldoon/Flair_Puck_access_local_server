# type: ignore
import json
import os
import shutil
from datetime import datetime
from random import random
from time import sleep
from typing import Tuple
from pathlib import Path
import re

import pytest

from playwright.sync_api import (
    APIRequestContext,
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    Route,
    Request,
    expect,
    Locator,
)
from modules.easy import HelpMethods
from modules.locators import Locators
from modules.constants import UiConstants

##### MAIN CONFTEST PART I: PYTEST AND PLAYWRIGHT SESSION #####


utcnow = datetime.utcnow()
timestamp = utcnow.strftime("%Y-%m-%d_%H-%M-%SZ")
info = None


def pytest_runtest_setup(item):
    """PyTest standard pre-test setup hook.
    We're using it to make sure we have clean network and trace folders.
    """
    global info
    base_dir = os.path.splitext(item.path)[0]

    # TODO: make less hacky
    if info is None or info["trace_dir"] != base_dir.replace("tests", "traces"):
        info = {
            "test_dir": "/" + os.path.join(*base_dir.split("/")[:-2]),
            "trace_dir": base_dir.replace("/tests/", "/traces/"),
            "network_dir": base_dir.replace("/tests/", "/network/"),
        }
        dirs = {"TRACES": info["trace_dir"], "HARS": info["network_dir"]}
        for asset, dir in dirs.items():
            if os.path.exists(dir):
                for fn in os.listdir(dir):
                    filepath = os.path.join(dir, fn)
                    # TODO: convert from local to utc
                    mdatetime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if utcnow < mdatetime:
                        continue
                    try:
                        shutil.rmtree(filepath)
                    except OSError:
                        os.remove(filepath)
            else:
                if not os.path.exists(os.path.dirname(dir)):
                    print(f"=====CREATING {asset[:-1]} DIR=====")
                    os.makedirs(os.path.dirname(dir))
                os.makedirs(dir)
        sleep(0.5)


def pytest_sessionfinish(session, exitstatus):
    """Standard PyTest session teardown hook.
    We're using it to add timestamps to har files.
    """
    if info is not None and "network_dir" in info.keys():
        if os.path.exists(f'{info["network_dir"]}/hars.zip'):
            fn, ext = os.path.splitext(f'{info["network_dir"]}/hars.zip')
            os.rename(f'{info["network_dir"]}/hars.zip', f"{fn}.{timestamp}.zip")


def load_from_json(filename: str) -> dict:
    with open(filename) as fh:
        return json.load(fh)


@pytest.fixture()
def env() -> dict:
    """The env.json file relevant to the test type, parsed."""
    return load_from_json(f"{info['test_dir']}/env.json")


@pytest.fixture()
def settings() -> dict:
    """The settings.json file relevant to the test type, parsed."""
    return load_from_json(f"{info['test_dir']}/settings.json")


@pytest.fixture()
def browser_type_launch_args(settings: dict) -> dict:
    """Settings to create a playwright.BrowserType"""
    return settings["browser_type_settings"]


@pytest.fixture()
def browser_context_args(settings: dict) -> dict:
    """Settings to create a playwright.BrowserContext"""
    bcs = settings["browser_context_settings"]
    bcs["record_har_path"] = Path(info["network_dir"]) / "hars.zip"
    return bcs


@pytest.fixture()
def other_settings(settings: dict) -> dict:
    """Settings for Browser object and Playwright defaults."""
    return settings["other_settings"]


# Refer to readme for more info on settings.
@pytest.fixture()
def browser_type(other_settings, playwright) -> BrowserType:
    return getattr(playwright, other_settings["browser"])


@pytest.fixture()
def test_name() -> str:
    tn = os.environ["PYTEST_CURRENT_TEST"].split(":")[-1].split(" ")[0]
    return tn


@pytest.fixture(scope="function")
def context(
    playwright: Playwright,
    browser_type: BrowserType,
    browser_type_launch_args: dict,
    browser_context_args: dict,
    other_settings: dict,
    test_name: str,
):
    """Produce playwright.BrowserContext for the test."""
    device = playwright.devices[other_settings["device"]]
    browser = browser_type.launch(**browser_type_launch_args)
    context = browser.new_context(**browser_context_args, **device)
    context.set_default_timeout(other_settings["timeout"])
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    context.tracing.stop(path=f"{info['trace_dir']}/{test_name}.{timestamp}.trace.zip")
    context.close()


@pytest.fixture(autouse=True)
def testenv(env):
    return {
        "env": "qa",
        "url": {
            "qa": {
                "site": env["url"]["site"],
                "api": env["url"]["api"]
            }
        }
    }


@pytest.fixture(autouse=True, scope="function")
def page_and_api(context: BrowserContext):
    """Provide a Tuple of playwright.Page and playwright.APIRequestContext.
    These two will be constant through a given test, and if not used, Playwright may create a new Page.
    """
    page = context.new_page()
    api = context.request
    yield (page, api)


@pytest.fixture(autouse=True)
def easy(page_and_api: Tuple[Page, APIRequestContext]) -> HelpMethods:
    return HelpMethods(*page_and_api)


@pytest.fixture(autouse=True)
def locators(page_and_api: Tuple[Page, APIRequestContext]) -> Locators:
    return Locators(page_and_api[0])


@pytest.fixture(autouse=True)
def constants() -> UiConstants:
    return UiConstants()


##### MAIN CONFTEST PART II: FLAIR UI UTILITIES #####


@pytest.fixture(autouse=True)
def standard_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Admin-Mode": "true",
    }

@pytest.fixture(autouse=True)
def disable_setup_mode(page_and_api: Tuple[Page, APIRequestContext], testenv, standard_headers):
    (_, api) = page_and_api
    api_url = testenv['url'][testenv['env']]['api']
    me = api.get(f'{api_url}/api/me', headers=standard_headers)
    default_structure = me.json()['data']['relationships']['default-structure']['data']['id']
    setup_mode_off_payload = {
        "data": {"type": "structures", "attributes": {"setup-mode": False}}
    }
    for _ in range(3):
        get_structure = api.get(f'{api_url}/api/structures/{default_structure}', headers=standard_headers)
        if get_structure.ok:
            break
        sleep(2) # sometimes we get rogue 500s on this call (probably worth looking into)
    if not get_structure.json()['data']['attributes']['setup-mode']:
        def_struct_patch = api.patch(f'{api_url}/api/structures/{default_structure}', headers=standard_headers, data=setup_mode_off_payload)
        assert def_struct_patch.ok
        sleep(5) # wait for disable setup mode to propagate


@pytest.fixture()
def puck_client_id_and_secret(page_and_api: Tuple[Page, APIRequestContext], standard_headers):
    """Method factory to get the Puck API OAuth client id and secret."""
    (_, api) = page_and_api

    def _puck_client_id_and_secret(api_url, sid):
        structure_info = api.get(f"{api_url}/api/structures/{sid}", headers=standard_headers)
        structure_response = structure_info.json()
        return (
            structure_response["data"]["attributes"]["puck-client-id"],
            structure_response["data"]["attributes"]["puck-client-secret"],
        )

    return _puck_client_id_and_secret


class Puck:
    """Represent a mocked Puck.

    Attributes
    ----------

    api_root : str
        The base of the API URL (e.g. https://api-ft.flair.co)
    client_id : str
        The Puck API OAuth Client ID for this puck / structure.
    client_secret : str
        The Puck API OAuth Client Secret for this puck / structure.
    puck_id : str
        The UUID of the Puck as stored in our database.
    puck_desired_state : str
        The hex code of the desired state for status payloads. I stole this from the API script.
    request_context : APIRequestContext
        The playwright.APIRequestContext object to use for API calls.
    version : int
        Version of Puck API to use, for status payloads.
    auth_token : str
        The OAuth access token to use with this session of Puck API.

    Methods
    -------

    get_access_token(context)
        Auth with OAuth to populate auth_token. Return the response payload as a dict.
    post_puck_status(context)
        Post a relatively standard Puck status payload. Return bool (True is OK).
    confirm_puck_ir_codes_download(context)
        Make a GET call to the Puck API IR status download endpoint. Return response headers as a dict.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        request_context: APIRequestContext,
        is_gateway=True,
        env_name="qa",
        puck_id=None,
    ):
        self.api_root = "https://api-qa.flair.co"
        if env_name.startswith("prod"):
            self.api_root = "https://api.flair.co"
        elif env_name.startswith("feat") or env_name.startswith("ft"):
            self.api_root = "https://api-ft.flair.co"
        elif env_name.startswith("dev") or env_name.startswith("test"):
            self.api_root = "http://localhost:5000"
        # Creating pseudo-random UUIDs that shouldn't collide, but contain test date info
        if puck_id is None:
            uuid_date_part = utcnow.strftime("%Y-%m%d-%H%M")
            micros = utcnow.strftime("%S%f")
            randpart_top = f"{str(random())[2:]:08}"
            randpart_end = f"{str(random())[2:]:04}"
            self.puck_id = f"{randpart_top[:8]}-{uuid_date_part}-{micros}{randpart_end[:4]}"
        else:
            self.puck_id = puck_id
        self.desired_state_id = "37f0"
        self.version = 8
        self.auth_token = None
        self.request_context = request_context
        self.client_id = client_id
        self.client_secret = client_secret
        self.iap = is_gateway
        self.default_status = {
            "puck_statuses": [
                {
                    "id": self.puck_id,
                    "tem": 2200,
                    "pre": 10000,
                    "rss": -42,
                    "svo": 330,
                    "hum": 60,
                    "lig": 40,
                    "bpu": 0,
                    "dsi": 53886,
                    "rec": 0,
                    "fww": 85,
                    "dte": 2500,
                    "dsi": int(self.desired_state_id, 16),
                    "iap": self.iap,
                }
            ],
            "vent_statuses": [],
        }

    def get_access_token(self) -> dict:
        """Populates self.auth_token with OAuth access token from Puck API."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "Flair Puck 1.0",
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        endpoint = f"{self.api_root}/oauth/token"
        response = self.request_context.post(endpoint, headers=headers, form=data)
        response_data = response.json()
        self.auth_token = response_data["access_token"]
        return response_data

    def post_puck_status(self) -> bool:
        """Uses POST on the sensor-readings endpoint to send a standard status payload."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Flair Puck 1.0",
            "Authorization": f"Bearer {self.auth_token}",
        }
        endpoint = f"{self.api_root}/puck-api/sensor-readings?version=4"
        response = self.request_context.post(endpoint, headers=headers, data=self.default_status)
        return response.ok

    def change_puck_status(self, updates: dict) -> dict:
        """Given a set of changes, update the puck status payload to match them"""
        for k in updates.keys():
            if k in self.default_status.keys():
                for i in range(len(self.default_status[k])):
                    self.default_status[k][i] |= updates[k][i]
                if len(updates[k]) > len(self.default_status[k]):
                    self.default_status[k].extend(updates[k][len(self.default_status[k]) :])
        return self.default_status

    def confirm_puck_ir_codes_download(self) -> dict:
        """Uses GET on the <puck-id>/ir-codes endpoint to confirm that IR codes are downloaded."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/plain",
            "User-Agent": "Flair Puck 1.0",
            "Authorization": f"Bearer {self.auth_token}",
        }
        endpoint = f"{self.api_root}/puck-api/{self.puck_id}/ir-codes-with-metadata"
        response = self.request_context.get(endpoint, headers=headers)
        with open('puck_codes', 'w') as ofh:
            ofh.write(response.body().decode())
        return response.body()

    def request_system_state(self, additional_pucks=[], vents=[]) -> dict:
        """Request the system state"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Flair Puck 1.0",
            "Authorization": f"Bearer {self.auth_token}",
        }
        endpoint = f"{self.api_root}/puck-api/system-state?version={self.version}"
        data = {
            "puck_uuids": [p.puck_id for p in additional_pucks] + [self.puck_id],
            "vent_uuids": [v.vent_id for v in vents]
        }
        system_state_info = self.request_context.post(endpoint, headers=headers, data=data)
        print('system-state call:', system_state_info.json())
        print(system_state_info.status_text)
        return system_state_info.json()


@pytest.fixture()
def get_puck(puck_client_id_and_secret, page_and_api: Tuple[Page, APIRequestContext]):
    """Method factory for initializing a Puck object."""
    (_, api_context) = page_and_api

    def _get_puck(api_url: str, sid: str, env_name: str, is_gateway=True, puck_id=None) -> Puck:
        (client_id, client_secret) = puck_client_id_and_secret(api_url, sid)
        return Puck(client_id, client_secret, api_context, is_gateway, env_name, puck_id)

    return _get_puck

class Vent:
    """Represent a mocked Vent.

    Attributes
    ----------

    api_root : str
        The base of the API URL (e.g. https://api-ft.flair.co)
    puck_api_access_token:
        The OAuth token for PuckAPI for this structure.
    vent_id : str
        The UUID of the Puck as stored in our database.
    request_context : APIRequestContext
        The playwright.APIRequestContext object to use for API calls.
    version : int
        Version of Puck API to use, for status payloads.

    Methods
    -------

    post_vent_status(context)
        Post a relatively standard Vent status payload. Return bool (True is OK).
    """

    def __init__(
        self,
        request_context: APIRequestContext,
        api_root: str,
        puck_api_access_token: str,
        vent_id=None
    ):
        self.api_root = api_root
        # Creating pseudo-random UUIDs that shouldn't collide, but contain test date info
        if vent_id is None:
            uuid_date_part = utcnow.strftime("%Y-%m%d-%H%M")
            micros = utcnow.strftime("%S%f")
            randpart_top = f"{str(random())[2:]:08}"
            randpart_end = f"{str(random())[2:]:04}"
            self.vent_id = f"{randpart_top[:8]}-{uuid_date_part}-{micros}{randpart_end[:4]}"
        else:
            self.vent_id = vent_id
        self.desired_state_id = "37f0"
        self.version = 4
        self.request_context = request_context
        self.puck_api_access_token = puck_api_access_token

    def post_vent_status(self) -> bool:
        """Uses POST on the sensor-readings endpoint to send a standard status payload."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Flair Puck 1.0",
            "Authorization": f"Bearer {self.puck_api_access_token}",
        }
        data = {
            "vent_statuses": [
                {
                    "id": f"{self.vent_id}",
                    "tem": 1900,
                    "pre": 10000,
                    "rss": -42,
                    "svo": 330,
                    "pop": 100,
                    "mrt": 1300,
                }
            ]
        }
        endpoint = f"{self.api_root}/puck-api/sensor-readings?version=4"
        response = self.request_context.post(endpoint, headers=headers, data=data)
        return response.ok

@pytest.fixture()
def get_vent_from_puck(page_and_api: Tuple[Page, APIRequestContext]):
    """Method factory for initializing a Vent object from an existing Puck."""
    (_, api_context) = page_and_api

    def _get_vent(api_url: str, puck_obj: Puck, vent_id=None) -> Vent:
        return Vent(
            request_context=api_context,
            api_root=puck_obj.api_root,
            puck_api_access_token=puck_obj.auth_token,
            vent_id=vent_id
        )

    return _get_vent

@pytest.fixture()
def add_room(auth: Tuple[Page, APIRequestContext]):
    """Method factory: Walk through the UI steps to set up a room."""
    (page, _) = auth

    def _add_room(room: dict, demo_type: str, is_ecobee: bool):
        enter_custom_name = page.get_by_text("Enter Custom Name")
        expect(enter_custom_name).to_be_visible()
        enter_custom_name.click()
        page.locator("[type=text]").fill(room["name"])
        page.get_by_role("button", name="Next").click()
        expect(page.get_by_text("Power on any additional Flair puck(s)")).to_be_visible()
        page.get_by_role("button", name="Next").click()
        page.get_by_role("checkbox").first.click()
        page.get_by_role("button", name="Next").click()

        if demo_type == "integrations" and not is_ecobee:
            with page.expect_request(
                lambda rq: rq.method == "PATCH" and "/api/rooms/" in rq.url
            ) as patch_rooms_request_info:
                room_id = patch_rooms_request_info.value.response().json()["id"]
            with page.expect_request(
                lambda rq: rq.method == "POST" and f"api/rooms/{room_id}/relationships/zones" in rq.url
            ) as zone_create_info:
                page.get_by_role("checkbox").first.click()
            assert zone_create_info.value.response().ok
            page.get_by_role("button", name="Next").click()

        if demo_type != "ir_device":
            expect(page.get_by_text("Power on your Flair Smart Vent(s)")).to_be_visible()
            page.get_by_role("button", name="Next").click()
            expect(page.get_by_text("Assign Smart Vents to this room")).to_be_visible()
            page.get_by_role("button", name="Skip").click()

            if demo_type == "integrations":
                if not is_ecobee:
                    with page.expect_request(
                        lambda rq: rq.method == "PATCH" and f"api/rooms/{room_id}/relationships/thermostat" in rq.url
                    ) as room_tstat_req_info:
                        # TODO: figure out what this selector is actually supposed to be
                        page.locator(".setup-container> ul> div:first").click()
                    assert room_tstat_req_info.value.response().ok
                    page.get_by_role("button", name="Next").click()

                expect(page.get_by_text("Please select any remote sensors in this room").first).to_be_visible()
                page.get_by_role("checkbox").first.click()
                page.get_by_role("button", name="Next").click()

            page.get_by_role("button", name="Complete Room").click()

    return _add_room


@pytest.fixture()
def add_ir_device(auth: Tuple[Page, APIRequestContext]):
    """Method factory: Walk through the UI steps to set up an IR device and add to a room."""
    (page, _) = auth

    def _add_ir_device(ir_device_type: str, tstat_obj: dict, room: dict, structure_id: str):
        page.get_by_text(ir_device_type).click()
        brand_on_screen = page.get_by_text(tstat_obj["brand"].title(), exact=True)
        if brand_on_screen.count() > 0:
            brand_on_screen.first.click()
        else:
            page.get_by_text("Other Brand").click()
            page.locator("[type=text]").first.fill(tstat_obj["name"])
            page.locator("[type=text]").last.click()
            page.get_by_placeholder("Search Brands").fill(tstat_obj["brand"])
            page.get_by_text(tstat_obj["brand"].title()).click()
            page.get_by_role("button", name="Add").click()

        expect(page.get_by_text("What room is this IR device in?")).to_be_visible()
        page.locator('label:has-text("Room Name")').click(force=True)
        enter_custom_name = page.get_by_text("Enter Custom Name")
        expect(enter_custom_name).to_be_visible()
        enter_custom_name.click()
        page.locator("[type=text]").fill(room["name"])
        page.get_by_role("button", name="Next").click()
        expect(page.get_by_text("Power on any additional Flair puck(s)")).to_be_visible()
        page.get_by_role("button", name="Next").click()
        page.get_by_role("checkbox").first.click()
        page.get_by_role("button", name="Next").click()

        # with page.expect_request(
        #     lambda rq: rq.method == "GET" and rq.url.endswith(f"api/structures/{structure_id}/pucks")
        # ) as get_pucks_info:
        #     pucks = get_pucks_info.value.response().json()["data"]
        #     first_four = pucks[0]["id"][:4]
        # page.get_by_text(first_four).click()
        # with page.expect_request(lambda rq: rq.method == 'POST' and 'api/rooms/' in rq.url) as assign_room_info:
        # assert assign_room_info.value.response().ok
        # page.get_by_role('button', name='Next').click()
        expect(page.get_by_text("Enter remote's model number")).to_be_visible()
        if "remote" in tstat_obj.keys() and tstat_obj["remote"]:
            page.locator("[type=text]").first.click(force=True)
            sleep(0.5)
            page.locator("[type=text]").first.fill(tstat_obj["remote"])
            page.get_by_text(tstat_obj["remote"]).first.click(timeout=20000)
            page.get_by_role("button", name="Next").click()
        else:
            page.get_by_role("button", name="Next").click()
            expect(page.get_by_text("Enter device's model number")).to_be_visible()
            page.get_by_role("button", name="Next").click()

    return _add_ir_device


@pytest.fixture()
def build_to_address(easy: HelpMethods):
    """Method factory: Create a new structure and return the SID"""

    def _build_to_address(page: Page, ui_base: str, home_name: str) -> str:
        page.goto(f"{ui_base}/h/new/")
        with page.expect_response(re.compile(r".*/api/structures/\d+$")) as structures_response_info:
            structures_response = structures_response_info.value.json()

        expect(page.get_by_role("heading", name="Create Home")).to_be_visible(timeout=20000)
        easy.text_visible("We're just a tap away")
        easy.next()

        easy.text_visible("Name your home")
        page.get_by_test_id("home-name-input").locator("input").fill(home_name)
        easy.next()

        easy.text_visible("Set your home location")
        page.get_by_text("Use my device's location").click()
        page.get_by_role("button", name="Confirm").click()

        easy.text_visible("Plug in your Puck")
        return structures_response["data"]["id"]

    return _build_to_address


@pytest.fixture()
def build_to_puck_connect(get_puck, puck_client_id_and_secret, easy: HelpMethods):
    """Method factory: Create a structure and connect a mocked Puck"""

    def _build_to_puck_connect(page: Page, env_name, ui_base, api_base, home_name):
        page.goto(ui_base)
        with page.expect_request_finished(lambda rq: api_base in rq.url and "accessible-structures" in rq.url):
            pass
        sleep(2.000)
        dialog = page.get_by_role("dialog").get_by_text("Unfinished Setup")
        if dialog.count() > 0:
            page.get_by_role("button").first.click()

        # NOTE: we're going through the 'front door' rather than visiting the setup address directly
        # page.get_by_text('Create a Home').click()
        create_home = "Create a Home"
        go_button = page.get_by_role("link", name=create_home)
        if not go_button.count():
            sleep(2)
            page.get_by_test_id("add-home-floating-plus").click()
            page.get_by_role("button", name="Add New Home").click()
        else:
            go_button.click()

        expect(page).to_have_url(re.compile(ui_base + r"/h/\d+/setup"))
        sid_re = re.compile(ui_base + r"/h/(\d+)/")
        sid = sid_re.search(page.url).group(1)

        puck = get_puck(api_base, sid, env_name)
        puck.get_access_token()

        #   We can re-route traffic called by the page or the browser anywhere we want, and fulfill requests
        # however we like. This is much like cy.intercept, but you don't have to call cy.wait--routing is automatic.
        def handle_puck_wifi(route: Route, request: Request):
            puck.post_puck_status()
            route.fulfill(status=200)

        # The context.route() call handles the incoming request to the Puck.
        page.context.route(re.compile("http://192.168.4.1/wifi/wifi.tpl"), handle_puck_wifi)

        # Not only is CORS navigation allowed, but we can interface with popups.
        page.once("popup", lambda popup: popup.close())

        # As mentioned previously, there are plenty of additional lambdas we could make to simplify this code.
        expect(page.get_by_role("heading", name="Create Home")).to_be_visible()
        easy.text_visible("We're just a tap away", {"timeout": 20000})
        easy.next()

        expect(page.get_by_text("Name your home")).to_be_visible()
        page.get_by_test_id("home-name-input").locator("input").fill(home_name)
        easy.next()

        easy.text_visible("Set your home location")
        page.get_by_text("Use my device's location").click()
        page.get_by_role("button", name="Confirm").click()

        easy.text_visible("Plug in your Puck", {"timeout": 30000})
        sleep(0.25)
        easy.next()

        easy.text_visible("Make your Puck a Gateway", {"timeout": 20000})
        easy.next()

        easy.text_visible("Wait until you see one of the following screens, then press next")
        easy.next()

        easy.text_visible("Connect your computer to “Flair WiFi xxxx”")
        easy.next()

        page.get_by_role("button", name="Puck shows this Icon").click()
        easy.text_visible("Waiting for Device to Connect")
        try:
            page.get_by_label("Close dialog 1").click()
        except:
            print('Klaviyo ads disabled, proceeding.')
        easy.text_visible("Connected! Tap Next To Continue", {"timeout": 30000})

        easy.next()
        return puck

    return _build_to_puck_connect

@pytest.fixture()
def connect_flair_devices(
    page_and_api: Tuple[Page, APIRequestContext],
    testenv,
    test_case,
    get_puck,
    get_vent_from_puck
):
    """
    Method factory: given a mocked home, testenv, intercept calls to /structure/<sid>/pucks
    and /structure/<sid>/vents, then return a dict with keys 'active_pucks', 'active_vents'
    """
    (page, api) = page_and_api
    base_url = testenv["url"][testenv["env"]]["site"]
    api_url = testenv["url"][testenv["env"]]["api"]

    def _connect_flair_devices(mock):
        active_pucks = {}
        active_vents = {}

        def handle_puck_vent(route: Route, request: Request):
            if 'vents' in request.url:
                route.fulfill(status=200, json={'data': list(mock.vents.values())})
            elif 'pucks' in request.url:
                route.fulfill(
                    status=200,
                    json={
                        'data': list(mock.gateway_pucks.values()) + \
                            list(mock.sensor_pucks.values())
                    }
                )

        page.route(f'{api_url}/api/structures/{test_case["structure_id"]}/pucks', handle_puck_vent)
        page.route(f'{api_url}/api/structures/{test_case["structure_id"]}/vents', handle_puck_vent)

        with page.expect_response(
            f'**/api/structures/{test_case["structure_id"]}/pucks'
        ) as puck_resp:
            with page.expect_response(
                f'**/api/structures/{test_case["structure_id"]}/vents'
            ) as vent_resp:
                page.goto(f'{base_url}/h/{test_case["structure_id"]}')
        for puck in puck_resp.value.json()["data"]:
            if puck["id"] not in active_pucks.keys():
                active_pucks[puck["id"]] = get_puck(
                    api_url=api_url,
                    sid=str(test_case["structure_id"]),
                    env_name=testenv["env"],
                    is_gateway=puck["attributes"]["is-gateway"],
                    puck_id=puck["id"],
                )
                active_pucks[puck["id"]].get_access_token()
                active_pucks[puck["id"]].post_puck_status()
        for vent in vent_resp.value.json()["data"]:
            if vent["id"] not in active_vents.keys():
                active_vents[vent["id"]] = get_vent_from_puck(
                    api_url=api_url,
                    puck_obj=list(active_pucks.values())[0],
                    vent_id=vent["id"]
                )
                active_vents[vent["id"]].post_vent_status()
        return {"active_pucks": active_pucks, "active_vents": active_vents}
    return _connect_flair_devices

##### MAIN CONFTEST PART III: API SHORTCUT UTILITIES #####


@pytest.fixture()
def api_create_structure(page_and_api: Tuple[Page, APIRequestContext], standard_headers):
    (page, api) = page_and_api

    def _api_create_structure(api_url: str, structure_name: str, payload_mod=None):
        headers = standard_headers
        me_response_info = api.get(f"{api_url}/api/me", headers=headers)
        me_response = me_response_info.json()
        user_id = me_response["data"]["id"]
        print("uid", user_id)
        payload = {
            "data": {
                "type": "structures",
                "attributes": {
                    "location-type": "address",
                    "country": "US",
                    "setup-complete": False,
                    "setup-mode": True,
                    "setup-step": "structure/name",
                    "home": True,
                    "temperature-scale": "F",
                },
                "relationships": {"admin-users": {"data": [{"id": str(user_id), "type": "users"}]}},
            }
        }
        if payload_mod is not None:
            for k in payload_mod.keys():
                if k in payload.keys():
                    for kk in payload_mod[k].keys():
                        payload[k][kk] |= payload_mod[k][kk]
        structures_endpoint = f"{api_url}/api/structures"
        structure_info = api.post(structures_endpoint, headers=headers, data=payload)
        structure_response = structure_info.json()
        sid = structure_response["data"]["id"]
        print("sid", sid)
        update_endpoint = f"{api_url}/api/structures/{sid}"
        update_payload = {
            "data": {
                "type": "structures",
                "attributes": {
                    "name": structure_name,
                    "time-zone": "America/Los_Angeles",
                    "latitude": 45.515232,
                    "longitude": -122.6783853,
                    "location": "100 SW Fake St",
                    "city": "Portland",
                    "state": "OR",
                    "zip-code": "97201",
                    "setup-step": "structure/gateway",
                },
            }
        }
        update_info = api.patch(update_endpoint, headers=headers, data=update_payload)
        assert update_info.ok
        return sid

    return _api_create_structure


@pytest.fixture()
def api_connect_puck_to_structure(page_and_api: Tuple[Page, APIRequestContext], puck_client_id_and_secret, get_puck):
    (_, api) = page_and_api

    def _api_connect_puck_to_structure(api_url, sid, env_name="ft"):
        puck = get_puck(api_url, sid, env_name)
        puck.get_access_token()
        puck.post_puck_status()

    return _api_connect_puck_to_structure
