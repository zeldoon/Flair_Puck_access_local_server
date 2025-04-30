from math import sqrt

MAX_SYMBOL_COUNT = 16
MAX_BIT_COUNT = 300

class Decoder:
    def __init__(self):
        self.bitstream = bytearray()
        self.symbol_timings = []
        self.idx = 0

    def get_byte(self, idx):
        return self.bitstream[idx]

    def get_byte_and_increment(self):
        byte = self.bitstream[self.idx]
        # print(self.idx, hex(byte))
        self.idx += 1
        return byte

    def combine_bytes(self, lower, higher):
        return (higher << 8) | lower

    def get_symbol(self, symbol_index):
        if len(self.symbol_timings) < symbol_index:
            # Why can't we decode these?
            # print(self.symbol_timings, symbol_index)
            return (0, 0)

        symbol = self.symbol_timings[symbol_index]
        return symbol[0], symbol[1]

    # NOTE: Maybe the sort should be more robust?
    # The mark sequence of 668, 672, 680, 676 and 656 are all close enough, so the
    # sequence should be sorted on the space value
    # [(668, 536), (672, 1632), (9016, 4460), (680, 19956), (676, 25000), (656, 39964)]
    def get_sorted_symbol_timings(self):
        return sorted(self.symbol_timings, key=lambda symbol_timing: symbol_timing[1])

    def decode(self, ir_code):
        self.symbol_timings = []
        ir_code_exclude_beef_prefix = ir_code[4:]
        padding_added = False
        if len(ir_code_exclude_beef_prefix) % 2:
            ir_code_exclude_beef_prefix += '0'
            padding_added = True

        self.bitstream = bytearray.fromhex(ir_code_exclude_beef_prefix)
        self.idx = 2
        bitstream_length = len(self.bitstream)
        byteCntHeader = 10

        if bitstream_length < byteCntHeader:
            print("Invalid bitstream: Header incomplete")
            return

        symbol_timing_count = self.get_byte_and_increment()
        press_frame_bit_count = self.get_byte_and_increment()
        repeat_frame_bit_count = self.get_byte_and_increment()
        release_frame_bit_count = self.get_byte_and_increment()
        toggle_t = self.get_byte_and_increment()
        toggle_s = self.get_byte_and_increment()

        byteCntTiming = symbol_timing_count * 4
        byteCntFirst = int((press_frame_bit_count + 1) / 2)
        byteCntRepeate = int((repeat_frame_bit_count + 1) / 2)
        byteCntRelease = int((release_frame_bit_count + 1) / 2)
        byteCntToggleT = int((toggle_t + 1) / 2)
        byteCntToggle = 1 if (toggle_s > 0) else 0 + byteCntToggleT * toggle_s
        expectedLen = byteCntHeader + \
                        byteCntTiming + \
                        byteCntFirst + \
                        byteCntRepeate + \
                        byteCntRelease + \
                        byteCntToggle

        if bitstream_length < expectedLen:
            print(f"bitstream length: {bitstream_length}, expected length: {expectedLen}")
            return

        if symbol_timing_count > MAX_SYMBOL_COUNT:
            print("ERROR: Too many symbols")
            return

        iTotalNumberOfBits = byteCntFirst + \
                                byteCntRepeate + \
                                byteCntRelease + \
                                (toggle_t * toggle_s)

        if iTotalNumberOfBits > MAX_BIT_COUNT:
            print("ERROR: Too many bits")
            return

        first_byte = self.get_byte(0)
        bRepeatMode = 1 if ((first_byte & 0x01) == 0x01) else 0;
        bUseCarrier = 1 if ((first_byte & 0x02) == 0x02) else 0;
        bMarkSpace = 1 if ((first_byte & 0x04) == 0x04) else 0;
        uRepeatCount = self.get_byte(1) & 0x0f
        wCarrierPeriod = self.combine_bytes(self.get_byte_and_increment(), self.get_byte_and_increment())

        # if uRepeatCount > 1:
            # print(f"Has repeats. Repeats: {uRepeatCount}, Press: {press_frame_bit_count}, Repeat: {repeat_frame_bit_count}")

        for i in range(0, symbol_timing_count):
            mark = self.combine_bytes(self.get_byte_and_increment(), self.get_byte_and_increment()) * 4
            space = self.combine_bytes(self.get_byte_and_increment(), self.get_byte_and_increment()) * 4
            self.symbol_timings.append((mark, space))

        raw_data = []
        while self.idx < bitstream_length:
            # print(f"GG: {self.idx}")
            symbol_idx_pair = self.get_byte_and_increment()
            first_symbol_idx = (symbol_idx_pair & 0xf0) >> 4
            raw_data.extend(self.get_symbol(first_symbol_idx))
            if self.idx != bitstream_length or not padding_added:
                second_symbol_idx = (symbol_idx_pair & 0xf)
                raw_data.extend(self.get_symbol(second_symbol_idx))

        for i in range(1, uRepeatCount):
            raw_data.extend(raw_data)

        return raw_data

MAX_ERROR = 2 ** 16
MATCH_THRESHOLD = 80
IR_CODE_FILE = '72f-heat-auto-swing.csv'

def get_root_mean_square_delta(raw_x, raw_y):
    if len(raw_x) != len(raw_y):
        return MAX_ERROR, MAX_ERROR, MAX_ERROR

    mark_space_delta = [(x - y) for x, y in zip(raw_x, raw_y)]
    mark_space_delta_squared = [delta * delta for delta in mark_space_delta]
    average_error = sqrt(sum(mark_space_delta_squared) / len(raw_x))
    min_error = sqrt(min(mark_space_delta_squared))
    max_error = sqrt(max(mark_space_delta_squared))
    return average_error, min_error, max_error

def get_symbol_timings_root_mean_square_delta(symbol_timings_x, symbol_timings_y):
    if len(symbol_timings_x) != len(symbol_timings_y):
        return MAX_ERROR, MAX_ERROR, MAX_ERROR

    symbol_timings_delta = [(x[0] - y[0], x[1] - y[1]) for x, y in zip(symbol_timings_x, symbol_timings_y)]
    symbol_timings_delta_squared = [sqrt(delta[0] * delta[0] + delta[1] * delta[1]) for delta in symbol_timings_delta]
    average_error = sqrt(sum(symbol_timings_delta_squared) / len(symbol_timings_x))
    min_error = sqrt(min(symbol_timings_delta_squared))
    max_error = sqrt(max(symbol_timings_delta_squared))
    return average_error, min_error, max_error

'''
Super weird looking IR Code:
"6c472c5a-96c1-4c5a-a82d-88dcb362342e",beef02010512400000000d0007b005c007b0033016c039f017b008f0c7a006a182110001001101001101100100100000000000000000000100000100100110100000001100000000100000000000000000000000000000000000010000000000000000000011010000321100010011010011011001001000000000000000000001000001001001101000000011000000001000000000000000000000000000000000000100000000000000000000110100004
Symbols: [(180252, 196628), (180252, 49164), (196696, 245988), (180316, 245792), (164636, 164888)]

"98c485d9-c7b0-4854-9c6d-66a91bdbe845",beef02010512400000000d0007a005c00790034016403a7017c008b0c7c006a182110001001101001101100100100000000000000000000100000100100110100000000011000111100000000000000000000000000000000000010000000000000001110011010000321100010011010011011001001000000000000000000001000001001001101000000000110001111000000000000000000000000000000000000100000000000000011100110100004

Trane Code:
"Raw: (419) 9016, -4464, 676, -532, 680, -552, 656, -1624, 680, -1628, 684, -548, 652, -556, 652, -556, 656, -548, 648, -536, 676, -1656, 656, -1624, 680, -528, 680, -528, 680, -552, 648, -556, 652, -556, 656, -552, 656, -548, 652, -556, 652, -552, 656, -552, 660, -1620, 680, -1628, 676, -556, 652, -556, 656, -548, 648, -1636, 680, -1624, 676, -1636, 680, -552, 656, -1624, 680, -556, 652, -552, 656, -1624, 680, -552, 656, -19960, 680, -528, 672, -560, 648, -556, 656, -552, 656, -552, 648, -556, 652, -556, 652, -552, 660, -548, 648, -560, 652, -552, 656, -552, 656, -548, 652, -556, 652, -1628, 676, -1632, 680, -552, 648, -560, 648, -556, 656, -552, 656, -548, 652, -556, 652, -556, 652, -552, 660, -548, 652, -552, 656, -552, 656, -524, 676, -556, 652, -556, 656, -1624, 676, -556, 656, -39968, 9020, -4460, 680, -524, 684, -552, 648, -1632, 684, -1624, 676, -556, 656, -552, 656, -548, 652, -556, 652, -556, 652, -1628, 676, -1632, 680, -528, 684, -548, 648, -556, 656, -552, 656, -548, 652, -556, 652, -556, 652, -552, 648, -560, 648, -556, 656, -1628, 672, -1632, 684, -524, 684, -548, 652, -556, 652, -1628, 684, -1624, 680, -1628, 676, -1632, 680, -1628, 676, -556, 652, -528, 684, -1624, 676, -556, 656, -19956, 684, -548, 660, -548, 652, -556, 652, -552, 656, -552, 648, -560, 648, -556, 656, -552, 656, -548, 652, -556, 652, -556, 652, -552, 648, -532, 680, -552, 656, -552, 656, -552, 648, -556, 652, -556, 656, -548, 648, -560, 652, -556, 652, -552, 656, -552, 648, -556, 652, -556, 656, -548, 648, -560, 652, -556, 652, -552, 656, -552, 648, -556, 652, -1628, 676, -39976, 9016, -4464, 676, -532, 680, -552, 656, -552, 648, -556, 652, -556, 652, -552, 660, -548, 648, -556, 656, -552, 656, -552, 656, -548, 652, -556, 652, -552, 660, -548, 648, -560, 652, -552, 656, -552, 656, -548, 652, -556, 652, -556, 656, -548, 648, -564, 648, -552, 656, -552, 656, -548, 652, -556, 652, -552, 660, -548, 648, -560, 652, -1628, 684, -524, 676, -1628, 684, -524, 684, -1624, 680, -528, 680, -19960, 680, -524, 676, -556, 652, -556, 656, -548, 660, -548, 652, -556, 652, -552, 656, -552, 648, -556, 652, -556, 656, -552, 656, -548, 652, -556, 652, -552, 656, -552, 648, -560, 648, -556, 656, -552, 656, -552, 648, -556, 652, -528, 680, -552, 660, -548, 648, -556, 656, -552, 656, -552, 648, -556, 652, -556, 652, -552, 648, -1632, 680, -528, 684, -1624, 680, "
Encoded: beef020106d200000000d000a4008900a6009701ce085b04a6007d13aa006a18a6000927200110000011000000000011000111010010300000000000000110000000000000010520011000001100000000001100011111001030000000000000000000000000000000152000000000000000000000000000001010103000000000000000000000000000001014

Ameristar Code:
"Raw: (279) 9020, -4456, 684, -1624, 680, -528, 680, -552, 648, -1632, 680, -524, 676, -532, 676, -532, 680, -524, 684, -1628, 676, -528, 680, -524, 676, -1632, 680, -528, 672, -532, 680, -528, 680, -524, 684, -524, 676, -556, 652, -528, 684, -524, 672, -532, 680, -1628, 676, -1632, 680, -524, 684, -524, 676, -556, 652, -528, 684, -1624, 676, -1632, 684, -520, 676, -1660, 656, -548, 652, -556, 652, -1628, 684, -524, 676, -19960, 684, -524, 684, -524, 676, -528, 680, -528, 684, -548, 648, -532, 680, -552, 656, -552, 648, -556, 652, -528, 680, -528, 684, -520, 676, -556, 656, -552, 656, -1624, 680, -1628, 676, -556, 652, -556, 652, -528, 684, -520, 676, -532, 680, -528, 680, -552, 648, -556, 652, -556, 656, -524, 684, -548, 652, -556, 652, -528, 680, -552, 648, -556, 652, -556, 656, -39964, 9016, -4464, 680, -552, 656, -524, 676, -532, 680, -524, 684, -548, 652, -556, 652, -528, 680, -552, 648, -532, 676, -556, 656, -556, 652, -548, 652, -528, 680, -552, 660, -520, 676, -560, 652, -552, 656, -552, 648, -556, 652, -528, 684, -524, 684, -524, 676, -528, 680, -528, 680, -524, 676, -556, 656, -552, 656, -528, 672, -556, 652, -1628, 684, -524, 676, -1656, 660, -520, 676, -1660, 656, -524, 684, -19952, 680, -528, 680, -524, 684, -524, 676, -532, 680, -552, 656, -524, 676, -556, 652, -528, 680, -552, 660, -548, 648, -532, 680, -552, 656, -548, 652, -528, 680, -528, 680, -524, 676, -532, 676, -556, 656, -524, 676, -528, 680, -528, 680, -528, 684, -548, 648, -556, 656, -524, 684, -548, 652, -528, 680, -528, 680, -524, 676, -1632, 680, -528, 684, -1624, 676, "
Encoded: beef0201068c00000000d000a7008600a8009801ce085b04aa007d13a9006a18a400072721001000010010000000001100001101001030000000000000011000000000000000052000000000000000000000000000001010103000000000000000000000000000001014
'''

if __name__ == '__main__':
    decoder = Decoder()
    raw_data_1 = decoder.decode('beef0201068c00000000d000a7008600a8009801ce085b04aa007d13a9006a18a400072721001000010010000000001100001101001030000000000000011000000000000000052000000000000000000000000000001010103000000000000000000000000000001014')
    sorted_symbol_timings_1 = decoder.get_sorted_symbol_timings()
    print(sorted_symbol_timings_1)

    with open(IR_CODE_FILE, 'r') as f:
        f.readline()
        for line in f:
            id, ir_code = line.strip().split(',')
            # print(f"Processing {id}")
            raw_data_2 = decoder.decode(ir_code)
            sorted_symbol_timings_2 = decoder.get_sorted_symbol_timings()
            if not raw_data_2:
                print("Decode Failure")
                continue

            average_error, min_error, max_error = get_symbol_timings_root_mean_square_delta(sorted_symbol_timings_1, sorted_symbol_timings_2)
            if average_error != MAX_ERROR:
                # print(f"{id}: error = {average_error}, {min_error}, {max_error}")
                pass
            if average_error < MATCH_THRESHOLD:
                if len(raw_data_1) == len(raw_data_2):
                    print(f"Match found: {id}")
                else:
                    print(f"Similar symbol timings but mismatched lengths: Original {len(raw_data_1)}, Matched {len(raw_data_2)}")

