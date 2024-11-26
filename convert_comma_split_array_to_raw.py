"""
convert a comma separated array to raw binary file
"""

import sys

def convert_comma_split_array_to_raw(array_file, raw_file):
    with open(array_file, 'r') as f:
        # read two bytes at a time
        array_data = f.read().split(',')
        with open(raw_file, 'wb') as g:
            for data in array_data:
                # convert to signed char and write to file
                c = int(data)
                g.write(bytes([c]))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python convert_comma_split_array_to_raw.py <array_file> <raw_file>')
        sys.exit(1)
    convert_comma_split_array_to_raw(sys.argv[1], sys.argv[2])