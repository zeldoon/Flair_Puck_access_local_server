from typing import Tuple
import json
import pytest
from playwright.sync_api import Page, APIRequestContext
from random import random, shuffle
from modules.ir_decode import Decoder, get_root_mean_square_delta
from time import sleep
from csv import DictReader
from datetime import datetime


def test_change_set_point(
    page_and_api: Tuple[Page, APIRequestContext],
    send_and_call_for_codes,
    confirm_same_code,
    access_token,
    get_puck,
    select_beef_codes_from_puck_obj,
    interpret_metadata,
    configure_room_by_settings,
    raw_string_to_code_list,
    env
):
    TS_FORMAT = '%Y-%m-%dT%H_%M_%SUTC'
    sheet_codes = {}
    sheet_settings = {}
    with open('hardware/impecca/impecca_spread') as csvfile:
        reader = DictReader(csvfile, dialect='excel-tab')
        for i,row in enumerate(reader):
            if row['FAN'] == '--':
                continue
            settings = {
                "mode": row["MODE"],
                "power": "non-specific ON",
                "fan_speed": f"Fan {row['FAN'].title()}",
                "swing_on": row["SWING"] == "ON",
                "temperature": f"{row['TEMPERATURE']}F"
            }
            sheet_code_strs = row['RAW_MARK_SPACE'].split(')')[1][:-1].split(', ')
            sheet_code = [abs(int(symbol)) for symbol in sheet_code_strs]
            sheet_codes[i+9] = sheet_code
            sheet_settings[i+9] = settings

    with open('hardware/impecca/impecca_metas_and_indices.csv') as csvfile:
        reader = DictReader(csvfile)
        index_to_meta = {
            int(line['code_index']) + 1: line['metadata_encoded'] for line in reader
        }

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

    """Test-test of IR code downloading"""
    (page, api) = page_and_api
    api_url = env['url']['api']
    print('Enabling fast report...')
    do_fr_call()
    puck = get_puck(
        api_url=api_url,
        sid='4388',
        env_name='qa',
        is_gateway=True,
        puck_id='55c89d47-cf51-5916-81b6-5c9e8848e6c1'
    )
    decoder = Decoder()

    puck.get_access_token()


    def do_patch_call(set_point):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Admin-Mode": "admin",
        }
        payload = {
            "data": {
                "type": "rooms",
                "attributes": {
                    "set-point-c": f_to_c(set_point),
                    "active": "true"
                },
            }
        }
        print(f'sending the following to https://api-qa.flair.co/api/rooms/{ROOM}:')
        print(json.dumps(payload, indent=2))
        return api.patch(
            f"https://api-qa.flair.co/api/rooms/{ROOM}", headers=headers, data=payload
        )


    def _patch_room_impecca():
        sleep(2)
        print(f'sending set point of {TEMP}F --')
        pcall = do_patch_call(TEMP)
        print(pcall.status_text)
        sleep(8)

    indices = list(index_to_meta.keys())
    print("\nWe have a list of all desired states that exist in the codeset, in hexadecimal. Shuffling the list.")
    shuffle(indices)
    metas = [index_to_meta[ind] for ind in indices]
    interpretations = [interpret_metadata(m) for m in metas]
    db_codes = select_beef_codes_from_puck_obj(puck, interpretations)
    shorts = []
    for i in range(25):
        if interpretations[i]['mode'].lower() == 'fan' or 'F' not in interpretations[i]['temperature']:
            continue
        print('Index of this state in the codeset:', indices[i])
        configure_room_by_settings(api_url=api_url, room=ROOM, settings=metas[i])
        TEMP = interpretations[i]['temperature'][:-1]
        codes = send_and_call_for_codes(_patch_room_impecca, 60)
        idi = {}
        iditer = 0
        while not idi and iditer < 6:
            sys_state = puck.request_system_state()
            idi = sys_state['pucks'][0]['idi']
            iditer += 1
            sleep(10)
        print('Received system state idi:', idi)
        if not idi:
            continue
        recv_code = idi['04'][0]['cde']
        recv_meta = index_to_meta[recv_code]
        print('\nThe current system-state indicates that we sent this code:', recv_code)
        correct_code = db_codes[i]
        if recv_meta == metas[i]:
            print("Metadata from the sent code matches the code we tried to send")
        else:
            print("Metadata from the sent code DOES NOT match the code we tried to send.", end=" ")
            print(f'Actual sent metadata is {recv_meta}')
            print("Fetching correct code for that metadata.")
            correct_code = select_beef_codes_from_puck_obj(puck, [interpret_metadata(recv_meta)])[0]
            print("Actual state is ", interpret_metadata(recv_meta))
            print("Actual beef code is:", correct_code)
        rcs = raw_string_to_code_list(codes[0])
        long_found = False
        print('\nIterating over all the codes received from the IR receiver unit:')
        for code in rcs:
            print(f' - Found code with {len(code)} symbols')
            if 197 < len(code) < 202:
                long_found = True
                result = confirm_same_code(decoder.decode(correct_code), code)
                print('Received the following code from IR receiver:')
                print(code)
                if result:
                    print('Codes appear to match.')
                else:
                    print('\n!!!!!!!!!')
                    print('CODE DOES NOT MATCH EXPECTATION')
                    for line, sheet_code in sheet_codes.items():
                        found = False
                        if confirm_same_code(code, sheet_code):
                            print(f'Code appears to match line {line} from the spreadsheet, with these settings:')
                            print(json.dumps(sheet_settings[line], indent=2))
                            print('\nexpected these settings:')
                            print(json.dumps(interpretations[i], indent=2))
                            found = True
                            break
                    if not found:
                        print('!!Code did not match anything in the spreadsheet')
            else:
                shorts.append((datetime.utcnow().strftime(TS_FORMAT), recv_meta, code))

        if not long_found:
            print('***Failed to receive valid code from receiver')
        print("=== ---- === ---- ===")
    for short in shorts:
        print(short)
