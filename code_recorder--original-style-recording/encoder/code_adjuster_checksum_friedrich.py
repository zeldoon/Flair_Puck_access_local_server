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
    for i in range(0, 6):
        code_byte = code_data[i*8:i*8+8]
        code_byte = code_byte[::-1]
        checksum_sum += int(code_byte, 2) & 0xFF
    # Some Friedrich codes require a +55 magic bit, found mentioned online
    # checksum_sum += 0x55
    checksum_sum = checksum_sum & 0xFF
    calculated_checksum = format(checksum_sum, '08b')
    calculated_checksum = calculated_checksum[::-1]
    return calculated_checksum


def calc_checksum_carrier(code_data):
    checksum_sum = 0
    for i in range(0, 4):
        code_byte = code_data[i*8:i*8+8]
        checksum_sum += int(code_byte, 2)
    checksum_sum = checksum_sum & 0xFF
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
        if idx > 0:
            old_beef = str(code['Data'])
            print('-----------------------------')
            print(old_beef)
            code_data = old_beef[57:105]
            recorded_checksum = old_beef[105:113]
            print(code_data)
            print(recorded_checksum)
            calculated_checksum = calc_checksum(code_data)
            if str(recorded_checksum) != str(calculated_checksum):
                print('ERROR!!!!!!!!!!!!!!!!!!!')
            else:
                print('Match.')

            code_data = code_data[0:33] + '1' + code_data[34:]
            calculated_checksum = calc_checksum(code_data[0:])
            new_beef = old_beef[0:57] + code_data + calculated_checksum + '3'
            print(new_beef)
            code['Data'] = new_beef

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



