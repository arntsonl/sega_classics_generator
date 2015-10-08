import struct, sys
from lzss import *

# Rotate left: 0b1001 --> 0b0011
rol = lambda val, r_bits, max_bits: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
 
# Rotate right: 0b1001 --> 0b1100
ror = lambda val, r_bits, max_bits: \
    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))
 
max_bits = 32
offset = 0

def checkSig(buf):
	global offset
	found = False
	if buf[0:8] == 'PSCD\x71\x89\x53\x12':
		found = True
	offset += 8
	return found

def getLong(buf):
	global offset
	ret = struct.unpack("I", buf[offset:offset+4])[0]
	offset = offset + 4
	return ret

# Sega's decryption algorithm
def decryptPak(buf, key, size):
	outBuf = ''
	staticKey = '\x6B\xC3\xC7\x6B\x83\xBB\x83\xC7\xC5\xBB\xD1\xAB\x2B'
	eax = int(0)
	ebx = int(0)
	ecx = int(key)
	edx = int(0)
	arg2 = 0
	for i in xrange(0, size):
		arg2 = arg2 % 0xd
		eax = ord(staticKey[arg2])
		arg2 += 3 
		ecx = rol(ecx, 3, max_bits)
		eax += 0x17
		eax = eax >> 1
		edx = ecx
		edx = edx & 0x7
		edx = edx + eax
		ebx = ecx
		ebx = ebx & 1
		ebx = ebx - eax
		edx = edx ^ ebx
		ebx = ecx
		ebx = ebx & 7
		edx = edx & 0xf
		ebx = ebx + eax
		edx = edx ^ ebx
		tmp = ord(buf[i])
		tmp = tmp ^ edx
		outBuf += chr(tmp)
	return outBuf
	
print 'Sega Genesis & Mega Drive Classics :: Pak Extractor'
print ' Ported by : Lucipher'
print ' Original code: Luigi Auriemma'
# http://aluigi.altervista.org/papers/bms/others/sega_classics.bms
print '---------------------------------------------------'
	
if len(sys.argv) != 2:
	print 'Usage: extract_pak <pak name>'
	quit()
f = open(sys.argv[1], 'rb')
buffer = f.read()
f.close()

if checkSig(buffer) == False:
	print 'Not a valid Sega Genesis / Mega Drive Pak'
	quit()

pscd_size = getLong(buffer)
pscd_zsize = getLong(buffer)
key = getLong(buffer)

# Xor our key with the magic number
key = key ^ 0x75a3bd72
offset = 0x2c
size = 0x30 # read out our name to make sure everything is working
memory_file = buffer[offset:offset+size]
offset += size # move the offset forward
name = decryptPak(memory_file, key, size)
print 'Found Game: %s'%(name.strip('\x00'))

offset += 4 # actual data bits (what is the 4 byte buffer fill??)
size = len(buffer) - offset # size of our data

if size != pscd_zsize:
	print 'Invalid Sega Genesis / Mega Drive Pak - Bad Length'
	quit()

memory_file = buffer[offset:]
data = decryptPak(memory_file, key, size)
decrypt_data = unlzss(data, pscd_zsize, pscd_size)

fo = open(name.strip('\x00')+'.bin','wb')
# finally, swap 16
for i in xrange(0, pscd_size/2):
	fo.write(decrypt_data[i*2+1])
	fo.write(decrypt_data[i*2])
fo.close()

print 'Saved to %s'%(name.strip('\x00')+'.bin')


