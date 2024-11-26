"""
read a raw pcm file and split it into two channels
"""

import sys

# channel 0: offset 0, 2, 4, ...
# channel 1: offset 1, 3, 5, ...
def split_channels(raw_file, left_channel, right_channel):
    with open(raw_file, 'rb') as f:
        with open(left_channel, 'wb') as g:
            with open(right_channel, 'wb') as h:
                bytes = f.read(2)
                while bytes:
                    g.write(bytes)
                    bytes = f.read(2)
                    h.write(bytes)
                    bytes = f.read(2)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: python split-channels.py <raw_file> <left_channel> <right_channel>')
        sys.exit(1)
    split_channels(sys.argv[1], sys.argv[2], sys.argv[3])
