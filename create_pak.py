import struct, sys
from lzss import *

# our custom pak key
PAK_KEY = 0x18DF3A11

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
def encryptPak(buf, key, size):
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
	
if len(sys.argv) != 4:
	print 'Usage: create_pak <bin name> <game name> <pak name>'
	quit()


outputBuffer = 'PSCD\x71\x89\x53\x12'

# open up our bin file
f = open(sys.argv[1], 'rb')
buffer = f.read()
f.close()
outputBuffer = outputBuffer + struct.pack('l', len(buffer)) # pscd_size (fill in later)

# swap 16
# bufferArray = list(buffer)
# for i in xrange(0, len(bufferArray)/2):
# 	tmp = bufferArray[i*2]
# 	bufferArray[i*2] = bufferArray[i*2+1]
# 	bufferArray[i*2+1] = tmp
# buffer = ''.join(bufferArray)
	
# lzss compress our swap-16 bin file
encrypt_data = compress(buffer)
outputBuffer = outputBuffer + struct.pack('l', len(encrypt_data)) # pscd_zsize (fill in later)
outputBuffer = outputBuffer + '\x11\x3A\xDF\x18' # 0xDEADBEEF

# don't know what these are
outputBuffer = outputBuffer + '\x00\x00\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

# Xor our key with the magic number
key = PAK_KEY ^ 0x75a3bd72

# encrypt the name
if len(sys.argv[2]) > 0x30:
   print 'Name too long'
   
name = sys.argv[2]
for i in range(len(sys.argv[2]), 0x30):
   name = name + '\x00'

encryptName = encryptPak(name, key, 0x30)
print "Encrypted name"
      
outputBuffer = outputBuffer + encryptName

# what is this? checksum? please not
outputBuffer = outputBuffer + '\x00\x00\x00\x00'

# write our encrypted data
outputBuffer = outputBuffer + encrypt_data
	
out = open(sys.argv[3], 'wb')
out.write(outputBuffer)



