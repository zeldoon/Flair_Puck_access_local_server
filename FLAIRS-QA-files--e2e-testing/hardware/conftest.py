import pytest
import json
import os
from datetime import datetime, timezone
from time import sleep
import boto3
import re
from typing import Tuple
from playwright.sync_api import BrowserContext, Page, APIRequestContext, expect
from modules.ir_decode import Decoder, get_root_mean_square_delta

# pytest_plugins = ["feature.conftest"]

CODE_TIMEOUT = 100
BUCKET_NAME = 'ir-testing-reads'
TS_FORMAT = '%Y-%m-%dT%H_%M_%SUTC'

# The auth fixture logs in, yields the Page and the APIRequestContext associated with it.
#  It then logs out as teardown.


@pytest.fixture(autouse=True)
def auth(page_and_api: Tuple[Page, APIRequestContext], env):
    """Authenticate via UI, yield (page, api) Tuple, log out as teardown."""
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
    page.evaluate('window.localStorage = ""')

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

@pytest.fixture(scope='session')
def s3_client():
    """Provide S3 Client"""
    return boto3.client('s3')

@pytest.fixture(scope='session')
def s3_session():
    """Provide S3 Resource"""
    return boto3.resource('s3')

@pytest.fixture(scope='session')
def ir_bucket(s3_session):
    """Provide S3 Bucket"""
    return s3_session.Bucket(BUCKET_NAME)

@pytest.fixture()
def call_for_codes(s3_client, tmp_path):
    """Factory: Provide 'call' file as a signal for the receiver script to respond"""
    def _call(start_time, timeout):
        call_fn = start_time.strftime(f'log/%Y-%m-%d/call-{TS_FORMAT}')
        local_fn = tmp_path / call_fn.split('/')[-1]
        with open(local_fn, 'w') as fh:
            fh.write(str(timeout))
        s3_client.upload_file(local_fn, BUCKET_NAME, call_fn)
    return _call

@pytest.fixture()
def retrieve_codes_after_start(ir_bucket):
    """Factory: Collect raw codes from 'codes' file provided by receiver script"""
    def _retrieve_codes(start_time, min_files):
        today = start_time.strftime('%Y-%m-%d')
        codes_after_start = []
        bucket_check = ir_bucket.objects.filter(Prefix=f'log/{today}/codes-{today}')
        if min_files >= sum(map(lambda x:1, bucket_check)):
            return []
        for file in bucket_check:
            if datetime.strptime(file.key.split('/')[-1], f'codes-{TS_FORMAT}') > start_time:
                these_codes = file.get()['Body'].read()
                codes_after_start.append(these_codes.decode())
        return codes_after_start
    return _retrieve_codes

@pytest.fixture()
def send_and_call_for_codes(call_for_codes, retrieve_codes_after_start, ir_bucket):
    """
    Factory: Given a callable and a timeout, call for a code from the receiver script,
    then execute the callable and retrieve the IR codes from AWS. The receiver script
    should wait for the timeout, then post the codes to the S3 bucket for retrieval.
    """
    def _send_and_call(callable, timeout: int):
        start_time = datetime.utcnow()
        right_start = start_time.strftime(TS_FORMAT)
        print(f'calling for codes: {timeout}s from {right_start}')
        call_for_codes(start_time, timeout)
        sleep(5)
        today = start_time.strftime('%Y-%m-%d')
        bucket_check = ir_bucket.objects.filter(Prefix=f'log/{today}/codes-{today}')
        min_files = sum(map(lambda x: 1, bucket_check))
        callable()
        for _ in range(CODE_TIMEOUT):
            sleep(1)
            new_codes = retrieve_codes_after_start(start_time, min_files)
            if len(new_codes):
                sleep(3)
                return new_codes
        raise TimeoutError(f'IR Codes not received within specified timeout: {CODE_TIMEOUT}s')
        return None
    return _send_and_call

@pytest.fixture()
def raw_string_to_code_list():
    def _prep_string(codestr):
        raw_codestrs = [code.strip() for code in codestr.split('\n') if code.strip()]
        outcodes = []
        for cs in raw_codestrs:
            if 'Raw: (' in cs and not 'Raw: (0)' in cs:
                outcodes.append([abs(int(c)) for c in cs.split(')')[1].split(',') if c.strip()])
        return outcodes
    return _prep_string

@pytest.fixture()
def confirm_same_code():
    """Use mean difference of roots to calculate whether two raw codes are the same."""
    def _confirm_code(code_a, code_b):
        same_thousand = lambda x, y: abs((float(x) / 1000.0) - (float(y) / 1000.0)) < 1.0
        if len(code_a) < 3 or len(code_b) < 3:
            return False
        code_a = [abs(int(c)) for c in code_a]
        code_b = [abs(int(c)) for c in code_b]
        if not same_thousand(code_a[0], code_b[0]):
            if same_thousand(code_a[1], code_b[0]):
                del(code_a[0])
            elif same_thousand(code_a[0], code_b[1]):
                del(code_b[0])
        if not same_thousand(code_a[-1], code_b[-1]):
            if same_thousand(code_a[-1], code_b[-2]):
                del(code_b[-1])
            elif same_thousand(code_a[-2], code_b[-1]):
                del(code_a[-1])
        avg_error, _, max_error = get_root_mean_square_delta(code_a, code_b)
        if avg_error < 55.0 and max_error < 170.0:
            return True
        return False
    return _confirm_code

@pytest.fixture()
def set_download_flag_from_puck_id(page_and_api, standard_headers, env):
    """Factory: set download flag on every hvac unit associated with given puck"""
    (_, api) = page_and_api
    api_root = env['url']['api']
    def _set_download_flag(puck_id):
        pucks_resp = api.get(
            f"{api_root}/api/pucks/{puck_id}",
            headers=standard_headers
        )
        hvac_unit_ids = [unit['id'] for unit in pucks_resp.json()['data']['relationships']['hvac-units']['data']]
        for hvac_unit_id in hvac_unit_ids:
            dl_flag_resp = api.patch(
                f'{api_root}/api/hvac-units/{hvac_unit_id}',
                headers=standard_headers,
                data={"data": {"type": "hvac-units", "attributes": {"redownload": "true"}}}
            )
            assert dl_flag_resp.ok
    return _set_download_flag

@pytest.fixture()
def interpret_metadata():
    modes = [
        'UNKNOWN',
        'AUTO',
        'HEAT',
        'COOL',
        'FAN',
        'DRY',
        'OTHER'
    ]
    fan_speeds = [
        'Fan Auto',
        'Fan Low',
        'Fan Medium',
        'Fan High'
    ]
    power_codes = [
        'OFF',
        'non-specific ON',
        'TOGGLE',
        'specific ON'
    ]
    temperatures = [f'{x}F' for x in range(40,101)] + [None, None, '--']
    def _interpret_metadata(hex_):
        hex_ = hex_.strip()
        num_of_bits = len(hex_) * 4
        bin_ = bin(int(hex_, 16))[2:].zfill(num_of_bits)
        mode_bits = bin_[:3]
        fan_speed_bits = bin_[3:6]
        swing_bit = bin_[6]
        requires_power_bit = bin_[7]
        temp_bits = bin_[8:14]
        power_bits = bin_[14:]
        return {
            'mode': modes[int(mode_bits, 2)],
            'fan_speed': fan_speeds[int(fan_speed_bits, 2)],
            'swing_on': bool(int(swing_bit)),
            'requires_power': bool(int(requires_power_bit)),
            'temperature': temperatures[int(temp_bits, 2)],
            'power': power_codes[int(power_bits, 2)]
        }
    return _interpret_metadata

@pytest.fixture()
def select_beef_codes_from_puck_obj(set_download_flag_from_puck_id, interpret_metadata):
    def _select_codes(puck, matches):
        set_download_flag_from_puck_id(puck.puck_id)
        codes_with_meta = [
            c.strip() for c in puck.confirm_puck_ir_codes_download().decode().split('\n') \
            if len(c.strip()) > 12
        ]
        matched_codes = []
        metas = {code[4:]: interpret_metadata(code[:4]) for code in codes_with_meta}
        for match in matches:
            for code, meta in metas.items():
                if match.items() <= meta.items():
                    matched_codes.append(code)
        return matched_codes
    return _select_codes

@pytest.fixture()
def configure_room_by_settings(page_and_api, standard_headers, interpret_metadata):
    (_, api) = page_and_api
    def _configure_room(api_url, room, settings):
        set_hc_mode_payload = lambda mode: {
            "data": {
                "type": "structures",
                "attributes": {
                    "structure-heat-cool-mode": mode.lower()
                }
            }
        }
        set_fan_speed_payload = lambda fan_speed: {
            "data": {
                "type": "hvac-units",
                "attributes": {
                    "default-fan-speed": fan_speed.upper()
                }
            }
        }
        set_swing_on_payload = lambda swing_on: {
            "data": {
                "type": "hvac-units",
                "attributes": {
                    "swing-auto": swing_on
                }
            }
        }
        if type(settings) == str:
            print()
            print('====START CONFIGURING ROOM TO MATCH METADATA====')
            print(f'Received metadata: {settings}')
            settings = interpret_metadata(settings)
            settings['fan_speed'] = settings['fan_speed'].split(' ')[-1]
        room_info = api.get(
            f'{api_url}/api/rooms/{room}',
            headers=standard_headers
        )
        room_json = room_info.json()
        sid = room_json['data']['relationships']['structure']['data']['id']
        hvac_id = room_json['data']['relationships']['hvac-units']['data'][0]['id']

        struct_end = f'{api_url}/api/structures/{sid}'
        hvac_end = f'{api_url}/api/hvac-units/{hvac_id}'
        print(f'sending the following to {struct_end}')
        print(json.dumps(set_hc_mode_payload(settings['mode']), indent=2))

        assert api.patch(
            struct_end,
            headers=standard_headers,
            data=set_hc_mode_payload(settings['mode'])
        ).ok

        print(f'sending the following to {hvac_end}')
        print(json.dumps(set_fan_speed_payload(settings['fan_speed']), indent=2))

        assert api.patch(
            hvac_end,
            headers=standard_headers,
            data=set_fan_speed_payload(settings['fan_speed'])
        ).ok

        print(f'sending the following to {hvac_end}')
        print(json.dumps(set_swing_on_payload(settings['swing_on']), indent=2))

        assert api.patch(
            hvac_end,
            headers=standard_headers,
            data=set_swing_on_payload(settings['swing_on'])
        ).ok
        print("====DONE CONFIGURING ROOM====\n")
    return _configure_room
