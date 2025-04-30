import re
from time import sleep
from typing import Tuple
from modules.easy import HelpMethods

import pytest

from playwright.sync_api import APIRequestContext, Page, Request, Route, expect


# @pytest.mark.parametrize("demo_name", ["integrations"])
@pytest.mark.parametrize("demo_name", ["integrations", "unsupported", "ir_device"])
def test_full_setup_process_wizard(
    auth: Tuple[Page, APIRequestContext],
    env,
    build_to_puck_connect,
    add_room,
    add_ir_device,
    demo_name,
    standard_headers,
    easy: HelpMethods,
    disable_setup_mode
):
    SUPPORTED_BRANDS = ["Ecobee", "Honeywell Home", "Google Nest",
                        "Honeywell Total Connect Comfort", "Carrier", "Bryant"]
    # TODO: Eventually this test could / should be parametrized so that code can be reused
    use_case = env["demo"][demo_name]
    #   Page and api handlers are returned from the auth fixture in conftest, to avoid having to acquire them
    # multiple times.
    (page, api) = auth

    # write any error console messages
    # page.on("console",
    #        lambda msg: print(f"error: {msg.text}") if msg.type == "error" else None)

    # alt: use this function as the callback for page.on() or page.once()
    def write_console_msg(msg):
        print(f"\nerror: {msg.text}\n") if msg.type == "error" else None

    puck = build_to_puck_connect(page, 'qa', env['url']['site'], env['url']['api'], env['demo']['home']['name'])
    sid_re = re.compile(env['url']['site'] + r"/h/(\d+)")
    structure_id = sid_re.search(page.url).groups(1)[0]
    me_info = api.get(f'{env["url"]["api"]}/api/me', headers=standard_headers)
    me_response = me_info.json()
    user_id = me_response['data']['id']

    #   We can make api calls directly through the browser context, without having to import lib requests.
    # The Playwright Response API provides methods and values for testing.
    for subcase in use_case:
        headers = standard_headers
        if demo_name == "integrations":
            integration_structures_url = (
                f"{env['url']['api']}/api/integrations/{subcase['manual_id']}/relationships/integration-structures"
            )

            for structure in subcase["structures"]:
                integration_structures_post_body = {
                    "data": [{"type": "integration-structures", "id": structure["id"]}]}
                integration_structures_post_response = api.post(
                    integration_structures_url, headers=headers, data=integration_structures_post_body
                )
                assert integration_structures_post_response.ok

        integration_url = re.compile(f".*/api/users/{user_id}/integrations")
        thermostat_url = re.compile(
            f".*/api/structures/{structure_id}/thermostats")
        int_struct_tstat_url = re.compile(
            ".*/api/integration-structures/.*/thermostats")
        easy.text_visible("What do you want Flair to control?")
        vendor = ""

        for hvac_device in subcase["hvac_devices"]:
            vendor = hvac_device["type"].title()
            if vendor != "Ir":
                with page.expect_request(integration_url) as integration_request_info:
                    page.get_by_text("Thermostat and Vents").click()
                    assert integration_request_info.value.response().ok

                easy.text_visible("Select your Thermostat")
                if vendor in SUPPORTED_BRANDS:
                    connected_to = page.locator(
                        "div", has_text=f"Connected to {vendor}")
                    # TECH DEBT: this may fail in future if test case has multiple thermostat types
                    # because it's just grabbing the first 'Use current account' available
                    if connected_to.count() > 0:
                        use_current = page.locator(
                            "div", has_text="Use current account")
                        if use_current.count() > 0:
                            use_current.click()
                        else:
                            page.get_by_text(vendor).first.click()
                    else:
                        with page.expect_popup(timeout=40000) as tstat_login_info:
                            page.get_by_role(
                                "button", name=re.compile(f".*{vendor}")).click()
                            # TODO: split out by vendor, right now we only do Ecobee
                        tstat_login = tstat_login_info.value
                        tstat_login.get_by_label("Email").fill(
                            hvac_device["tstat_portal_login"]["username"])
                        tstat_login.get_by_label("Password").fill(
                            hvac_device["tstat_portal_login"]["password"])
                        tstat_login.get_by_role(
                            "button", name="Sign in").click()
                else:
                    page.get_by_text("Other Thermostat").click()
                    page.locator("[type=text]").fill(hvac_device["name"])
                    easy.next()
                    page.locator("[type=text]").click()
                    page.get_by_placeholder("Search Brands").fill(
                        hvac_device["brand"])
                    page.get_by_role(
                        "button", name=hvac_device["brand"].title()).click()
                    easy.next()

                with page.expect_response(int_struct_tstat_url):
                    sleep(0.1)
                seen_structures = []
                for structure in [s for s in subcase["structures"] if s["enabled"]]:
                    if structure['name'] not in seen_structures:
                        page.get_by_text(structure["name"]).click()
                        seen_structures.append(structure['name'])
                easy.next()

                forced_air = page.get_by_text("Forced Air")
                try:
                    forced_air.wait_for(timeout=500)
                    forced_air.click()
                    easy.next()
                except:
                    pass

                how_many_vents = f"How many vents are in {hvac_device['name']}'s zone?"
                easy.text_visible(how_many_vents)
                page.locator("[type=number]").fill(
                    str(hvac_device["vent_count"]))
                easy.next()

                easy.text_visible(
                    "Need to add another Thermostat, Mini Split, Portable, or Window AC?")

                with page.expect_request(thermostat_url) as thermostat_request_info:
                    with page.expect_request(re.compile(".*api/structures/.*/rooms")) as rooms_request_info:
                        page.get_by_role(
                            "button", name="Done Adding Devices").click()
                        assert thermostat_request_info.value.response().ok
                        assert rooms_request_info.value.response().ok

            else:
                room = [r for r in env["demo"]["rooms"]
                        if r["id"] == hvac_device["room_id"]][0]
                add_ir_device(hvac_device["ir_device_type"],
                              hvac_device, room, structure_id)
                easy.text_visible("Waiting for puck to download codes...")
                puck.confirm_puck_ir_codes_download()

                expect(page.get_by_text("IR Setup Enabled")
                       ).to_be_visible(timeout=20000)
                easy.next()
                easy.text_visible("Wait until your Puck shows the IR Menu")
                easy.next()
                easy.text_visible("Your Puck has three IR beams")
                easy.next()
                easy.text_visible("Puck distance")
                easy.next()
                easy.text_visible(
                    "Test each model number until your unit beeps or responds")
                easy.next()
                easy.text_visible(
                    "Choose the model number that worked for your unit")

                page.locator("[type=text]").first.click()
                page.get_by_text(hvac_device["model"]).first.click()
                easy.next()
                page.get_by_text("Done Adding Devices").click()

        if any([tstat["type"] != "ir" for tstat in subcase["hvac_devices"]]):
            # all the rooms that match a room_id
            set_rooms = [
                room for room in env["demo"]["rooms"] if room["id"] in [t["room_id"] for t in subcase["hvac_devices"]]
            ]
            unset_rooms = [room for room in env["demo"]
                           ["rooms"] if room not in set_rooms]
            for room in set_rooms:
                room_text = "Create a new room" if room["id"] == 0 else "Add a New Room"
                with page.expect_request(re.compile(".*api/structures/.*/rooms")) as rooms_request_info:
                    page.get_by_text(room_text).click()
                    page.locator(
                        'label:has-text("Room Name")').click(force=True)
                    assert rooms_request_info.value.response().ok

                with page.expect_response(thermostat_url) as room_tstat_response_info:
                    add_room(room, demo_name, vendor.lower() == "ecobee")
                assert room_tstat_response_info.value.ok

            for room in unset_rooms:
                room_text = "Create a new room" if room["id"] == 0 else "Add a New Room"
                page.get_by_text(room_text).click()
                page.locator('label:has-text("Room Name")').click(force=True)
                add_room(room, demo_name, vendor.lower() == "ecobee")

        page.get_by_text("Finish Room Setup").click()
        # easy.text_visible('Structure in Setup Mode.')
        easy.text_visible("System Mode")

        if demo_name == "integrations":
            easy.next()
            easy.text_visible("Set Point Control")

        easy.next()
        easy.text_visible("Away Mode")

        easy.next()
        easy.text_visible("Determining Home or Away")
        easy.next()

        if demo_name == "integrations":
            easy.text_visible("Away Min/Max Temperatures")
            easy.next()

        if demo_name == "ir_device":
            easy.next()

        if demo_name == "unsupported":
            easy.text_visible("What mode is your thermostat in?")
            page.wait_for_load_state("domcontentloaded")
            page.get_by_text("Cooling").click()
            easy.next()

        easy.text_visible("Make This Your Primary Home?")
        easy.next()

        easy.text_visible("Support for your Flair System")
        easy.next()

        easy.text_visible("Setup Complete!")
        page.get_by_text("Finish Setup").click()
        page.wait_for_url(re.compile(
            env["url"]["site"] + r"/h/\d+\?skip-check=true"), timeout=20000)
        assert easy.any_text_visible("Home")
        delete_url = f'{env["url"]["api"]}/api/structures/{structure_id}'
        delete_response_info = api.delete(delete_url, headers=headers)
        assert delete_response_info.ok
