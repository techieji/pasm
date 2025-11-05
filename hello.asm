format ELF64 executable

segment readable executable
entry start

start:
    mov rdi, 1
    ;mov rsi, msg
    lea rsi, [msg]
    mov rdx, size
    mov rax, 1
    syscall

    mov rdi, 0
    mov rax, 60
    syscall

segment readable writable

msg db "Hello, world!", 10, 0
size = $ - msg
