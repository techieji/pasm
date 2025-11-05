import sys
import platform
from typing import Literal

if len(sys.argv) <= 1:
    print("Usage: pasm <filename>")
    exit(1)

out = open(sys.argv[1], 'wb')

BUILD_FORMAT: Literal['EXEC', 'LIB'] = 'EXEC'
PTR_SIZE = int(platform.architecture()[0][:2]) // 8

### ELF Header
out.write(b'\x7FELF')                                                     # Magic
out.write(b'\x01' if PTR_SIZE == 4 else b'\x02')     # 32 or 64 bit
out.write(b'\x01' if sys.byteorder == 'little' else b'\x02')              # byteorder
out.write(b'\x01')       # Mandatory 1
out.write(b'\x03')       # ABI kind (Linux or SYSV?, idk how to programmatically determine this)
out.write(b'\x00')       # Further ABI kind (Ignored for static Linux executables)
out.write(b'\x00' * 7)   # Padding bytes
out.write(b'\x00\x01' if BUILD_FORMAT == 'LIB' else b'\x00\x02')                  # Build format (duh...)
out.write(b'\x3E\x00')   # Architecture (either AMD x86 or ARM??? idk how to programmmatically ...)
out.write(b'\x01\x00\x00\x00')       # Mandatory 1
ENTRY = out.tell()
out.write(PTR_SIZE * b'\x00')     # Entry point
PHOFF = out.tell()
out.write(PTR_SIZE * b'\x00')     # Program header table offset
SHOFF = out.tell()
out.write(PTR_SIZE * b'\x00')     # Section header table offset
out.write(4 * b'\x00')            # Flags (no flags exist)
_SIZE = out.tell()
out.write(2 * b'\x00')            # Size of this header
_PHSIZE = out.tell()
out.write(2 * b'\x00')            # Program header size
_PHNUM = out.tell()
out.write(2 * b'\x00')            # Number of entries in program header table
out.write(b'\x28\x00' if PTR_SIZE == 4 else b'\x40\x00')                  # Section header table entry size
_SHNNUM = out.tell()
out.write(2 * b'\x00')            # Number of entries in section header table
_SHSTRNDX = out.tell()
out.write(2 * b'\x00')            # Index of section header with section names

print(out.tell())

out.flush()
out.close()
