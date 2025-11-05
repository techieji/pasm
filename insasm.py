opcodes = {
    ('mov', '64', 'lit'): b'\x48\xc7',
    ('syscall',): b'\x0f\x05'
}

reg = {
    'rax': b'\xc0',
    'rcx': b'\xc1',
    'rdx': b'\xc2',
    'rbx': b'\xc3',
    'rsp': b'\xc4',
    'rbp': b'\xc5',
    'rsi': b'\xc6',
    'rdi': b'\xc7',
}

def asm_command(mnemonic, *args):
    k = (mnemonic, *['64' if type(x) is str else 'lit' for x in args])
    op = opcodes[k]
    # TODO add typing and length checking!
    binargs = [reg[x] if type(x) is str else x.to_bytes(4, 'little') for x in args]
    return op + b''.join(binargs)

c = b''
c += (asm_command('mov', 'rdi', 1))
c += (asm_command('mov', 'rsi', 0x004010de))
c += (asm_command('mov', 'rdx', 15))
c += (asm_command('mov', 'rax', 1))
c += (asm_command('syscall'))
c += (asm_command('mov', 'rdi', 0))
c += (asm_command('mov', 'rax', 60))
c += (asm_command('syscall'))
print(c)
print(len(c))
