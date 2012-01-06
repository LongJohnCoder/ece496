#!/usr/bin/env python2.7

import sys
import serial
import optparse


def read_bitstream(filename=None, dump=False):
	values = list()

	# open file (or default to stdin)
	f = sys.stdin
	if filename is not None:
		f = open(filename)
	
	for line in f.readlines():
		if len(line) > 0 and line[0] != '#':
			parts = line.split(':')
			if len(parts) != 2:
				raise Exception, "unexpected format on line: " + line
			bits = int(parts[0])
			value = int(parts[1], 16)
			values.append((value, bits))

	if filename is not None:
		f.close()

	# print out binary string representation of the bitstream
	if dump:
		for x in values:
			print "{0:0{1}b}".format(x[0], x[1])
	
	return values


def serialize(values):
	bytelist = list()
	combined = "".join(["{0:0{1}b}".format(val, l) for val, l in values])

	if len(combined) % 8 != 0:
		combined = "{0:0{1}b}".format(0, 8 - len(combined) % 8) + combined

	for i in range(0, len(combined) - 1, 8):
		bytelist.append(int(combined[i:i+8], 2))

	return bytelist


def write_btye(value):
	for i in range(5):
		s.write(chr(value))
		read = s.read()
		if len(read) > 0:
			break
	else:
		print "no response for {0:d} {0:08b}!".format(value)
		return False

	read = ord(read)
	if read != value:
		print "value read doesn't match value sent!"
		print "{:08b} -> {:08b}".format(value, read)
		return False

	return True


parser = optparse.OptionParser()

parser.add_option("-f", "--file", dest="filename", type="string",
		default=None, help="bitstream file to open (default is stdin)")
parser.add_option("-d", "--device", dest="device", type="string",
		default="/dev/ttyUSB0", help="serial port device")
parser.add_option("-b", "--baud", dest="baud", type="int",
		default=115200, help="device baud rate")
parser.add_option("-t", "--timeout", dest="timeout", type="float",
		default=0.1, help="device write timeout")
parser.add_option("--dump", dest="dump", action="store_true",
		default=False, help="print binary bitstream")
parser.add_option("--dry", dest="dry", action="store_true",
		default=False, help="don't flash the bitstream (implies --dump)")

options, args = parser.parse_args(sys.argv)

if options.dry:
	options.dump = True

data = read_bitstream(options.filename, options.dump)

if options.dry:
	print "dry run read", len(serialize(data)), "bytes"
	sys.exit(0)

s = serial.Serial(options.device, baudrate=options.baud, timeout=options.timeout,
		bytesize=8, parity=serial.PARITY_EVEN)

bytes = 0
for value in serialize(data):
	if write_byte(value):
		bytes += 1
	else:
		print "failed to write complete bitstream"
		sys.exit(1)

print "wrote", bytes, "bytes to serial device"

