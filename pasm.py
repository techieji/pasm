import sys
import struct
import platform
import os

if len(sys.argv) <= 1:
    print("Usage: pasm <filename>")
    exit(1)

out = open(sys.argv[1], 'wb')

is_32 = platform.architecture()[0][:2] == '32'
is_little = sys.byteorder == 'little'

ENTRY = 0
PHOFF = 0
SHOFF = 0

# Documentation: https://www.man7.org/linux/man-pages/man5/elf.5.html
# ELF header: information needed for execution and context
ehdr_fmt = '@16sHHIPPPIHHHHHH'
# Program header: information for executables and SOs:
#    Describes all segments, which contain sections.
phdr_fmt = '@IPPPIIII' if is_32 else '@IIPPPLLL'   # pflags location is different!
# Section header: only used for in linking
shdr_fmt = '@IILPPLIILL'

def make_elf_header(entry, phoff, shoff, kind=2):
    """Makes the elf header section with the given parameters.

    Note that static libraries should (probably) be compiled with kind=1 and executables
    should be compiled with kind=2. SOs should be compiled with kind=3."""

    e_machine = 0x3e # AMD x86-64 (implement automatic lookup technique)
    e_ident = struct.pack('4s5c7x', b'\x7fELF', b'\x01' if is_32 else b'\x02',
                          b'\x01' if is_little else b'\x02', b'\x01', b'\x00', b'\x00')
    return struct.pack(ehdr_fmt, e_ident, kind, e_machine, 1, entry, phoff, shoff,
        0, struct.calcsize(ehdr_fmt), struct.calcsize(phdr_fmt),
        0,         # number of entries in program header table
        struct.calcsize(shdr_fmt),         # Size of Section header table entry
        0,         # number of entries in section header table
        0          # index of section header table for string table
    )

PF_X = 0x1
PF_W = 0x2
PF_R = 0x4
def make_program_header(segment: bytes, segment_offset: int, vaddr: int, kind=1, flags=PF_X|PF_R):
    """Makes a program header for a particular segment.

    Kind should be 1 for loadable segments; 3 for interpreter programs (the
    segment would contain a null-terminated string as the interpreer); others
    can be looked up in the docs.

    segment_offset is the location of the segment. vaddr is the address in virtual
    memory at which the segment will live."""
    filesz = memsz = len(segment)
    align = os.sysconf("SC_PAGE_SIZE")       # idk exactly why this is
    args = [kind, segment_offset, vaddr, filesz, memsz, align]
    args.insert(6 if is_32 else 1, flags)
    return struct.pack(phdr_fmt, *args)

header = make_elf_header(ENTRY, PHOFF, SHOFF)
out.write(header)

out.flush()
out.close()
