from typing import Tuple
import pytest
from playwright.sync_api import Page, APIRequestContext
from random import random
from modules.ir_decode import Decoder, get_root_mean_square_delta
from time import sleep


def test_change_set_point(
    page_and_api: Tuple[Page, APIRequestContext],
    send_and_call_for_codes,
    confirm_same_code,
    access_token,
    get_puck,
    select_beef_codes_from_puck_obj,
    env
):
    """Test-test of IR code downloading"""
    def do_fr_call():
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "fast-report": True,
            "interval": 2
        }
        api.post("https://api-qa.flair.co/api/reporting-intervals",
                 headers=headers,
                 data=payload)


    def f_to_c(f) -> float:
        return (float(f) - 32.0) / 1.8

    TEMP = None
    ROOM = '5104'

    (page, api) = page_and_api
    api_url = env['url']['api']
    puck = get_puck(
        api_url=api_url,
        sid='4388',
        env_name='qa',
        is_gateway=True,
        puck_id='78be5db8-a85b-52c1-73e8-b930d42906a8'
    )
    decoder = Decoder()

    puck.get_access_token()
    lasko_beef_75s = select_beef_codes_from_puck_obj(puck, [{'temperature': '75F'}])
    lasko_beef_79s = select_beef_codes_from_puck_obj(puck, [{'temperature': '79F'}])

    def _patch_room():
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Admin-Mode": "admin",
        }
        payload = {
            "data": {
                "type": "rooms",
                "attributes": {"set-point-c": 24, "active": "true"},
            }
        }

        payload['data']['attributes']['set-point-c'] = f_to_c(TEMP)
        api.patch(
            f"https://api-qa.flair.co/api/rooms/{ROOM}", headers=headers, data=payload
        )
        sleep(5)

    TEMP = 75
    first_code = send_and_call_for_codes(_patch_room, 40)
    found = False
    for code in lasko_beef_75s:
        found = found or confirm_same_code(decoder.decode(code), first_code)
    assert found

    TEMP = 79
    second_code = send_and_call_for_codes(_patch_room, 40)
    found = False
    for code in lasko_beef_79s:
        found = found or confirm_same_code(decoder.decode(code), first_code)
    assert found
