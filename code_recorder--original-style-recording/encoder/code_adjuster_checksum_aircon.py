# NOTE
# Use python code_adjuster.py [input file name] where the
# input file name is the txt file you want to adjust the
# IR codes and this will create an output file named
# [filename]-adjusted.txt in the same directory

import sys
import json
from collections import Counter
from pprint import pprint
from struct import *


def calc_checksum(code_data):
    checksum_sum = 0
    for i in range(0, 8):
        if i == 4:
            continue
        code_byte = code_data[i*8:i*8+8]
        code_byte = code_byte[::-1]
        checksum_sum += int(code_byte, 2) & 0x0F
    checksum_sum += 0x0A
    checksum_sum = checksum_sum & 0x0F
    calculated_checksum = format(checksum_sum, '04b')
    calculated_checksum = calculated_checksum[::-1]
    return calculated_checksum


def calc_checksum_carrier(code_data):
    checksum_sum = 0
    for i in range(0, 10):
        code_byte = code_data[i*8:i*8+8]
        checksum_sum = checksum_sum ^ int(code_byte, 2)
    calculated_checksum = format(checksum_sum, '08b')
    return calculated_checksum


def calc_checksum_carrier_2(code_data):
    checksum_sum = 0
    for i in range(0, 5):
        code_byte = code_data[i*8:i*8+8]
        checksum_sum = checksum_sum ^ int(code_byte, 2)
    calculated_checksum = format(checksum_sum, '08b')
    return calculated_checksum


def adjust_codes(file_to_adjust):
    print('START...')
    original_file = open(file_to_adjust, 'r')
    print('File to adjust: ', original_file.name)
    json_data = open(file_to_adjust).read()

    data = json.loads(json_data)
    
    codes = data['Codes']
    for idx, code in enumerate(codes):
        if idx > 1:
            old_beef = str(code['Data'])
            print('-----------------------------')
            print(old_beef)
            code_data_1 = old_beef[81:113] + old_beef[114:170]
            recorded_checksum_1 = old_beef[170:178]
            calculated_checksum_1 = calc_checksum_carrier(code_data_1)
            if str(recorded_checksum_1) != str(calculated_checksum_1):
                print('ERROR1!!!!!!!!!!!!!!!!!!!')

            code_data_2 = old_beef[179:227]
            recorded_checksum_2 = old_beef[227:235]
            calculated_checksum_2 = calc_checksum_carrier_2(code_data_2)
            if str(recorded_checksum_2) != str(calculated_checksum_2):
                print('ERROR2!!!!!!!!!!!!!!!!!!!')

            new_beef = old_beef[0:113] + '200000011000000000000000000000001000000000000000000000000' + old_beef[170:187] + '101' + old_beef[190:]
            print(new_beef)

            code_data_1 = new_beef[81:113] + new_beef[114:170]
            calculated_checksum_1 = calc_checksum_carrier(code_data_1)

            code_data_2 = new_beef[179:227]
            calculated_checksum_2 = calc_checksum_carrier_2(code_data_2)

            final_beef = new_beef[0:170] + calculated_checksum_1 + '2' + new_beef[179:227] + calculated_checksum_2 + '4'
            print(final_beef)

            code['Data'] = final_beef

    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)
    print('DONE.')


# MAIN PROGRAM

print('===================================')
print('THE ADJUSTER')
print('===================================')
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



