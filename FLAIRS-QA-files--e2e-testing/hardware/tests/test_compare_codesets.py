from typing import Tuple
import json
import pytest
from playwright.sync_api import Page, APIRequestContext
from random import random, shuffle
from modules.ir_decode import Decoder, get_root_mean_square_delta
from time import sleep
from csv import DictReader
from itertools import combinations

decoder = Decoder()

codeset_to_model = {
    '6d8029bf-5ba8-45cb-bb4b-81c01849a13f': 'Impecca R09B-BGE-F',
    '6a2b436e-ab80-4b4c-bcaa-e2b8dc1b3d2d': 'Pioneer RG10A4(D1)/BGEFU1-F',
    '4045970f-a516-462e-bcfe-de3a8206cb2a': 'Pioneer RG66B6(B)/BGEFU1-F'
}

def test_compare_codes(
    page_and_api: Tuple[Page, APIRequestContext],
    confirm_same_code,
    interpret_metadata,
    raw_string_to_code_list,
    env
):

    with open('hardware/impecca/impecca_pioneer_compare.csv') as csvfile:
        reader = DictReader(csvfile)
        codes = [{k: v for k,v in line.items()} for line in reader]

    metaset = list(set([line['metadata_encoded'] for line in codes]))
    for meta in metaset:
        print(f'------meta: {meta}------')
        matches = list(filter(lambda line: line['metadata_encoded'] == meta, codes))
        print('• Codesets that contain code:', ', '.join([m['hvac_codeset_id'] for m in matches]))
        if len(matches) < 3:
            missings = [
                c for c in codeset_to_model.keys() \
                if c not in [m['hvac_codeset_id'] for m in matches]
            ]
            print(" • The following models' codesets do not contain the codepoint/state:")
            for m in missings:
                print(f'  - {m}')

        combos = combinations(matches, 2)
        matched = True
        for combo in combos:
            a_code = decoder.decode(combo[0]['ir_code'])
            b_code = decoder.decode(combo[1]['ir_code'])
            a_name = codeset_to_model[combo[0]['hvac_codeset_id']]
            b_name = codeset_to_model[combo[1]['hvac_codeset_id']]
            if confirm_same_code(a_code, b_code):
                print(f" -- {a_name} and {b_name} match")
            else:
                matched = False
                print(f" !! {a_name} and {b_name} DO NOT match")
                print('    ' + combo[0]['ir_code'])
                print('    ' + combo[1]['ir_code'])
        if not matched:
            print('    state:')
            print(json.dumps(interpret_metadata(meta), indent=2))
        print(f'======================')
