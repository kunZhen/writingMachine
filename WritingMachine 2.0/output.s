	.text
	.file	"<string>"
	.globl	Main
	.p2align	4, 0x90
Main:
	.cfi_startproc
	movabsq	$x_position, %rax
	movl	$2, (%rax)
	mfence
	movabsq	$y_position, %rcx
	movl	$2, (%rcx)
	mfence
	movabsq	$pen_down, %rdx
	movb	$1, (%rdx)
	mfence
	addl	$4, (%rcx)
	mfence
	movl	$5, (%rax)
	mfence
	addl	$10, (%rax)
	mfence
	addl	$-4, (%rcx)
	mfence
	movb	$0, (%rdx)
	mfence
	addl	$-3, (%rax)
	mfence
	movb	$1, (%rdx)
	mfence
	movl	$5, (%rcx)
	mfence
	addl	$2, (%rcx)
	mfence
	retq
.Lfunc_end0:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
