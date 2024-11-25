	.text
	.file	"<string>"
	.globl	linea1
	.p2align	4, 0x90
linea1:
	.cfi_startproc
	retq
.Lfunc_end0:
	.cfi_endproc

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
	addl	$-4, (%rax)
	mfence
	movb	$1, (%rdx)
	mfence
	movl	$5, (%rcx)
	mfence
	addl	$2, (%rcx)
	mfence
	retq
.Lfunc_end1:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
