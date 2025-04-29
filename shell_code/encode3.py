import numpy as np
import pprint

import sys
import os
import subprocess
import struct

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn import metrics

warning_1 = 0 #Note: Mismatch between number of marks and spaces, padding last index
warning_2 = 0 #Note: Non-integer characters at end of output, deleting last index

def cluster_ir_codes(incoming_codes):
    if (len(incoming_codes) % 2):
        incoming_codes.append(25000)
        #print "Note: Mismatch between number of marks and spaces, padding last index"
        warning_2 = 1
    else:
        incoming_codes.pop(0)
        incoming_codes.append(25000)

    raw_codes = [incoming_codes]

    for i, raw_code in enumerate(raw_codes):
        # plt.figure()

        MARKS = np.array(raw_code[::2])
        SPACES = np.array(raw_code[1::2])
        plt.scatter(MARKS, SPACES)

        raw_code = np.array(raw_code)
        code = raw_code.reshape(int(len(raw_code) / 2), 2)
        X = code
        #print code

        db = DBSCAN(eps=200, min_samples=1).fit(X)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_
        # print core_samples_mask

        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
        mark_space_vals = {}
        for k, col in zip(unique_labels, colors):
            # print k, col
            if k == -1:
                # Black used for noise.
                col = 'k'

            class_member_mask = (labels == k)
            # print class_member_mask

            xy = X[class_member_mask & core_samples_mask]
            #plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
            #         markeredgecolor='k', markersize=14)

            centroid = np.mean(xy, axis=0)
            # print k, centroid
            e = xy - centroid
            e_average = np.sqrt(np.mean(np.square(e), axis=0))
            # print e_average

            xy = X[class_member_mask & ~core_samples_mask]
            # plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
            #          markeredgecolor='k', markersize=6)
            mark_space_vals[k] = (abs(centroid[0]), abs(centroid[1]))

        # print labels
        # plt.title('Plot: %d' % i)
        # plt.show()


        for i in range(0, len(mark_space_vals)):
            sum = int(mark_space_vals[i][0]) + int(mark_space_vals[i][1])
            mark_space_vals[i] = mark_space_vals[i] + (sum,)
        sorted_mark_space_vals = sorted(mark_space_vals.items(), key=lambda mark_space_vals: mark_space_vals[1][2])

        lookup = []
        for i in range(0, len(sorted_mark_space_vals)):
            lookup.append(tuple((i, sorted_mark_space_vals[i][0])))
        sorted_lookup = sorted(lookup, key=lambda lookup: lookup[1])

        sorted_labels = []
        
        for i in range(0, len(labels)):
            sorted_labels.append(sorted_lookup[labels[i]][0])

        #print sorted_mark_space_vals
        #print " "
        #print labels
        #print sorted_labels
        return (sorted_mark_space_vals, sorted_labels)

def get_data_without_command_timings(mark_space_vals):
    binary_vals = ''
    for index, val in enumerate(mark_space_vals):
        if len(mark_space_vals[val]) == 2:
            if index == 0:
                mark_space_vals[val] = (mark_space_vals[val][0], mark_space_vals[val][1], '0')
            elif index == 1:
                mark_space_vals[val] = (mark_space_vals[val][0], mark_space_vals[val][1], '1')
            elif index == 2:
                mark_space_vals[val] = (mark_space_vals[val][0], mark_space_vals[val][1], '0')
            else:
                #print val, mark_space_vals[val]
                mark_space_vals[val] = (mark_space_vals[val][0], mark_space_vals[val][1], '?')
        if index:
            if not index % 4:
                binary_vals += ' '
        binary_vals += mark_space_vals[val][2]
    #print binary_vals
    #print '\n0100 0000 0000 0100 0000 0001 0000 0000 1011 1100 1011 1101, 0x40040100bcbd'

    return hex(int(binary_vals.split('?')[0].replace(' ', ''), 2))

def write_preencoding_format_to_temp_file(mark_space_vals, encoded_payload, filename_fullpath):
    with open(filename_fullpath, 'w') as f:
        f.write("Header:1,1,0,1,210\n")
        f.write("Symbols:" + "|".join([str(int(value[0])) + "," + str(int(value[1])) for key, value in sorted(mark_space_vals.iteritems())]) + "\n")
        f.write("Payload:" + ','.join(str(i) for i in encoded_payload) + "\n")
    return filename_fullpath

def print_preencoding_format(mark_space_vals, encoded_payload):
    """Expects to not have 0 and 1 at the beginning and end of the encoded payload"""
    print("Header:1,1,0,1,210")
    print("Symbols:" + "|".join([str(int(value[0])) + "," + str(int(value[1])) for key, value in sorted(mark_space_vals.iteritems())]))
    print("Payload:" + ','.join(str(i) for i in encoded_payload))

def encode_to_uird_format_from_preencoding_file(preencoded_file):
    if sys.platform == "linux" or sys.platform == "linux2":
        command = "./ir-process-linux"
    elif sys.platform == "darwin":
        command = "./ir-process-mac"


    encoded_values = subprocess.Popen([command, "0", preencoded_file],
    				     stdout=subprocess.PIPE,
                                     cwd=os.path.dirname(os.path.realpath(__file__))).communicate()[0].split('\n')[1][0:-2]
    meta_data = {}
    meta_data['transcoded_command'] = encoded_values
    meta_data['binary_packed_data'] = ''.join([struct.pack("B", int(i, 16)) for i in encoded_values.split(', ')])
    return meta_data

def encode_to_uird(mark_spaces_clean):
    temp_filename = os.path.dirname(os.path.realpath(__file__)) + 'temp.txt'
    (mark_space_vals,encoded_payload) = cluster_ir_codes(mark_spaces_clean)
    write_preencoding_format_to_temp_file(mark_space_vals, encoded_payload, temp_filename)
    uird_encoded_command = encode_to_uird_format_from_preencoding_file(temp_filename)
    os.remove(temp_filename)
    data_without_timings = get_data_without_command_timings(mark_space_vals)
    #print data_without_timings
    return uird_encoded_command, data_without_timings

def encode_to_data_without_timing_info_from_raw_string(example_output):
    example_output = example_output.replace(' ', '').split(',')
    example_output[0] = example_output[0].split(')')[1]
    return encode_to_uird([int(i) for i in example_output])[1]

def encode_to_uird_from_raw_string(example_output):
    example_output = example_output.replace(' ', '').split(',')
    example_output[0] = example_output[0].split(')')[1]
    return encode_to_uird([int(i) for i in example_output])[0]

def encode_as_uird(mark_spaces_clean):
    (mark_space_vals,encoded_payload) = cluster_ir_codes(mark_spaces_clean)
    #print mark_space_vals
    #print encoded_payload

    # print magic header
    magic_header = "beef"
    final_output = magic_header

    # print control flags
    control_flags = "0201" # Need to be able to parse repeating patterns and report here
    final_output += control_flags

    # print control data
    num_timing_definitions = len(mark_space_vals)
    num_symbols_pressed_frame = len(encoded_payload) # Don't forget about repeating patterns!
    num_symbols_repeat_frame = 0
    num_symbols_release_frame = 0
    num_symbols_toggle_frame = 0
    num_toggle_sequences = 0
    carrier_period = 0xd000 # Hard coded for now
    final_output += "%02x" % num_timing_definitions
    final_output += "%02x" % num_symbols_pressed_frame
    final_output += "%02x" % num_symbols_repeat_frame
    final_output += "%02x" % num_symbols_release_frame
    final_output += "%02x" % num_symbols_toggle_frame
    final_output += "%02x" % num_toggle_sequences
    final_output += "%04x" % carrier_period

    # print symbol definitions
    #mark_space_values = mark_space_vals.values()
    mark_space_values = mark_space_vals
    #print mark_space_values
    for i in range(0, len(mark_space_vals)):
        if int(mark_space_values[i][1][0]) > (2**16):
            print("ERROR: Mark length longer than 16-bit")
        if int(mark_space_values[i][1][0]) > (2**16):
            print("ERROR: Space length longer than 16-bit")
        mark = int(mark_space_values[i][1][0] / 4)
        space = int(mark_space_values[i][1][1] / 4)
        final_output += struct.pack('<h', mark).hex()
        final_output += struct.pack('<h', space).hex()

    # print payload
    for i in range(0, len(encoded_payload)):
        final_output += str(encoded_payload[i])

    # print "\nEncoded Output:"
    # print final_output + "\n"
    return final_output

def encode_to_data_without_timing_info_from_recording(example_output):
    example_output = example_output.replace(bytes(' ', 'utf-8'), bytes('', 'utf-8')).split(bytes(',', 'utf-8'))
    length = example_output[0].split(bytes(')', 'utf-8'))[0]
    length2 = length.split(bytes('(', 'utf-8'))[1]
    example_output[0] = example_output[0].split(bytes(')', 'utf-8'))[1]
    output_int = []
    warning_1 = None
    warning_2 = None
    try:
        output_int = [int(i) for i in example_output]
    except:
        #print "Note: Non-integer characters at end of output, deleting last index"
        warning_1 = 1
        example_output.pop()
        output_int = [int(i) for i in example_output]
    #print output_int
    return encode_as_uird(output_int), length2, warning_1, warning_2
    
def encode_as_uird_with_repeat(mark_spaces_clean):
    (mark_space_vals,encoded_payload) = cluster_ir_codes(mark_spaces_clean)
    #print mark_space_vals
    #print encoded_payload

    # print magic header
    magic_header = "beef"
    final_output = magic_header

    # print control flags
    control_flags = "0202" # Need to be able to parse repeating patterns and report here
    final_output += control_flags

    payload_len = len(encoded_payload)
    first_half = encoded_payload[0:(payload_len/2)]
    second_half = encoded_payload[(payload_len/2):payload_len]

    if first_half[1:len(first_half)-1] == second_half[1:len(first_half)-1]:
        print('match!')
        encoded_payload = first_half
    else:
        print("Original payload:")
        print(encoded_payload)
        print("NO MATCH!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(first_half)
        print(second_half)

    # print control data
    num_timing_definitions = len(mark_space_vals)
    num_symbols_pressed_frame = 0 # Don't forget about repeating patterns!
    num_symbols_repeat_frame = len(encoded_payload)
    num_symbols_release_frame = 0
    num_symbols_toggle_frame = 0
    num_toggle_sequences = 0
    carrier_period = 0xd000 # Hard coded for now
    final_output += "%02x" % num_timing_definitions
    final_output += "%02x" % num_symbols_pressed_frame
    final_output += "%02x" % num_symbols_repeat_frame
    final_output += "%02x" % num_symbols_release_frame
    final_output += "%02x" % num_symbols_toggle_frame
    final_output += "%02x" % num_toggle_sequences
    final_output += "%04x" % carrier_period

    # print symbol definitions
    #mark_space_values = mark_space_vals.values()
    mark_space_values = mark_space_vals
    #print mark_space_values
    for i in range(0, len(mark_space_vals)):
        if int(mark_space_values[i][1][0]) > (2**16):
            print("ERROR: Mark length longer than 16-bit")
        if int(mark_space_values[i][1][0]) > (2**16):
            print("ERROR: Space length longer than 16-bit")
        mark = int(mark_space_values[i][1][0] / 4)
        space = int(mark_space_values[i][1][1] / 4)
        final_output += struct.pack('<h', mark).encode('hex')
        final_output += struct.pack('<h', space).encode('hex')

    # print payload
    for i in range(0, len(encoded_payload)):
        final_output += str(encoded_payload[i])

    # print "\nEncoded Output:"
    # print final_output + "\n"
    return final_output

def encode_to_data_without_timing_info_from_recording_with_repeat(example_output):
    example_output = example_output.replace(' ', '').split(',')
    length = example_output[0].split(')')[0]
    length2 = length.split('(')[1]
    example_output[0] = example_output[0].split(')')[1]
    output_int = []
    try:
        output_int = [int(i) for i in example_output]
    except:
        #print "Note: Non-integer characters at end of output, deleting last index"
        warning_1 = 1
        example_output.pop()
        output_int = [int(i) for i in example_output]
    #print output_int
    return encode_as_uird_with_repeat(output_int), length2, warning_1, warning_2
