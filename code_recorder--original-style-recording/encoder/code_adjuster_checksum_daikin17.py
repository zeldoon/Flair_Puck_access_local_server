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

def adjust_codes(file_to_adjust):
    original_file = open(file_to_adjust, "r")
    print("File to adjust: ", original_file.name)
    json_data = open(file_to_adjust).read()

    data = json.loads(json_data)
    
    codes = data['Codes']
    for idx, code in enumerate(codes):
        if idx > 0:
            old_beef = str(code['Data'])
            power = str(code['Power'])
            mode = str(code['Mode'])

            print("-----------------------------------")
            print('old_beef: ' + old_beef)
            if power == 'ON' and (mode == 'COOL' or mode == 'HEAT'):
                first_beef = old_beef[:91]
                last_beef = old_beef[115:]
                #mid_beef = first_beef + '000011000000000000000011' + last_beef # time 00:30, timer ON set for 00:30
                mid_beef = first_beef + '100101000000000000000011' + last_beef # time 00:29, timer ON set for 00:30
                print('mid_beef: ' + mid_beef)

                old_main_data = old_beef[75:139]
                checksum_sum = int(old_main_data[0:4][::-1], 2) + int(old_main_data[4:8][::-1], 2) + int(old_main_data[8:12][::-1], 2) + int(old_main_data[12:16][::-1], 2) + int(old_main_data[16:20][::-1], 2) + \
                                int(old_main_data[20:24][::-1], 2) + int(old_main_data[24:28][::-1], 2) + int(old_main_data[28:32][::-1], 2) + int(old_main_data[32:36][::-1], 2) + int(old_main_data[36:40][::-1], 2) + \
                                int(old_main_data[40:44][::-1], 2) + int(old_main_data[44:48][::-1], 2) + int(old_main_data[48:52][::-1], 2) + int(old_main_data[52:56][::-1], 2) + int(old_main_data[56:60][::-1], 2)
                checksum_sum = checksum_sum % 16
                recorded_checksum = int(old_main_data[60:64][::-1], 2)
                if checksum_sum == recorded_checksum:
                    print('Checksum match!')
                else:
                    print('ERROR!!!!!!!!!!')

                new_checksum = int(mid_beef[75:79][::-1], 2) + int(mid_beef[79:83][::-1], 2) + int(mid_beef[83:87][::-1], 2) + int(mid_beef[87:91][::-1], 2) + int(mid_beef[91:95][::-1], 2) + \
                                int(mid_beef[95:99][::-1], 2) + int(mid_beef[99:103][::-1], 2) + int(mid_beef[103:107][::-1], 2) + int(mid_beef[107:111][::-1], 2) + int(mid_beef[111:115][::-1], 2) + \
                                int(mid_beef[115:119][::-1], 2) + int(mid_beef[119:123][::-1], 2) + int(mid_beef[123:127][::-1], 2) + int(mid_beef[127:131][::-1], 2) + int(mid_beef[131:135][::-1], 2)
                new_checksum = new_checksum % 16
                print('checksum: ' + str(new_checksum))
                result_checksum = format(new_checksum, '04b')[::-1]
                new_beef = mid_beef[:135] + result_checksum + mid_beef[139:]
                code['Data'] = new_beef
            else:
                new_beef = old_beef
                print('Unchanged')
                code['Data'] = new_beef

    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)


# MAIN PROGRAM

print("===================================")
print("THE ADJUSTER")
print("===================================")
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



