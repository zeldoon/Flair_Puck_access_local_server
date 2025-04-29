# NOTE
# Use python encode_csv.py [input file name] where the
# input file name is the csv file you want to get encoded
# and this will create an output file named encoded.txt
# in the same directory

import encode
import sys
from collections import Counter

def encode_file(file_to_encode):
    encode_file = open(file_to_encode, "r")
    print("File to encode: ", encode_file.name)

    length_array = []
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    new_file_name = "encoded-"+my_list[1]+".txt"
    print("Output file:     " + new_file_name)
    output_file = open(new_file_name, "w")

    print("Formatting device metadata...")
    output_file.write("{\n")
    output_file.write("    \"Meta\": {\n")
    output_file.write("        \"Manufacturer\":\""+my_list[1]+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Model number\":\""+my_list[1]+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Unit type\":\""+my_list[1]+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Remote model\":\""+my_list[1]+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Description\":\""+my_list[1]+"\",\n")
    my_line = encode_file.readline()
    my_list = my_line.split(",")
    output_file.write("        \"Notes\":\""+my_list[1]+"\"\n")
    output_file.write("    },\n")
    my_line = encode_file.readline()
    my_line = encode_file.readline()

    print("Encoding raw data...")
    output_file.write("    \"Codes\": [\n")
    i = 0
    j = 0
    for line in encode_file.readlines():
        if (i == 0):
            i += 1
        else:
            output_file.write(",\n")
        my_list = line.split(",")
        output_file.write("        {\n")
        output_file.write("            \"Power\":\""+my_list[0]+"\",\n")
        output_file.write("            \"Temp Scale\":\""+my_list[1]+"\",\n")
        output_file.write("            \"Temperature\":\""+my_list[2]+"\",\n")
        output_file.write("            \"Fan\":\""+my_list[3]+"\",\n")
        output_file.write("            \"Swing\":\""+my_list[4]+"\",\n")
        output_file.write("            \"Mode\":\""+my_list[5]+"\",\n")
        raw_code = line.split("w:")[1]
        encoded_code,raw_length,warning_1,warning_2 = encode.encode_to_data_without_timing_info_from_recording(raw_code)
        length_array.append(int(raw_length))
        output_file.write("            \"Data\":\""+encoded_code+"\"\n")
        output_file.write("        }")
        print(encoded_code)
    output_file.write("\n    ]\n")

    output_file.write("}\n")
    encode_file.close()
    output_file.close()

    m = 0
    length_average = int(round(float(sum(length_array))/float(len(length_array)),0))
    count_most_common = Counter(length_array)
    most_common_length = count_most_common.most_common()[0][0]
    print("Most common length:")
    print(most_common_length)
    for k in length_array:
        if (length_array[m] == most_common_length):
            m += 1
        else:
            print("Warning: Line " + str(m + 1) + " symbol length does not match the most common length")
            m += 1
    if (warning_1 == 1):
        print("Note: There is data with mismatch between number of marks and spaces, padded last index")
    if (warning_2 == 1):
        print("Warning: Non-integer characters at end of output, deleting last index")

# MAIN PROGRAM

print("===================================")
print("THE ENCODER")
print("===================================")
my_encode_file = sys.argv[1]
encode_file(my_encode_file)



