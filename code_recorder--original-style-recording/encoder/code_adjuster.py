# NOTE
# Use python code_adjuster.py [input file name] where the
# input file name is the txt file you want to adjust the
# IR codes and this will create an output file named
# [filename]-adjusted.txt in the same directory

import sys
import json
from collections import Counter
from pprint import pprint

def adjust_codes(file_to_adjust):
    original_file = open(file_to_adjust, "r")
    print("File to adjust: ", original_file.name)
    json_data = open(file_to_adjust).read()

    data = json.loads(json_data)
    i = 0
    codes = data['Codes']
    for idx, code in enumerate(codes):
    	#print(i)
    	i+=1
        old_beef = str(code['Data'])
        print('Old: ' + old_beef)
        if idx > 1:
            code['Data'] = old_beef[0:86] + '0' + old_beef[87:]
        else:
            code['Data'] = old_beef
        #print('New: ' + code['Data'])
        
    output_name = str(original_file.name) + '-adjusted.txt'
    with open(output_name, 'w') as outfile:
        json.dump(data, outfile)


# MAIN PROGRAM

print("===================================")
print("THE ADJUSTER")
print("===================================")
codes_to_adjust = sys.argv[1]
adjust_codes(codes_to_adjust)



