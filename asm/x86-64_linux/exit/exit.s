.intel_syntax
.text
.global _start
_start:
	mov %rax, 60
	xor %rdi, %rdi
	mov %rdi, 69
	syscall
