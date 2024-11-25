	.text
	.file	"<string>"
	.globl	Main
	.p2align	4, 0x90
Main:
	.cfi_startproc
	mfence
	movabsq	$pen_down, %rax
	movb	$1, (%rax)
	mfence
	movabsq	$y_position, %rcx
	addl	$5, (%rcx)
	mfence
	movabsq	$x_position, %rdx
	addl	$10, (%rdx)
	mfence
	addl	$-4, (%rcx)
	mfence
	movb	$0, (%rax)
	mfence
	addl	$-3, (%rdx)
	mfence
	movb	$1, (%rax)
	mfence
	addl	$2, (%rcx)
	mfence
	retq
.Lfunc_end0:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
