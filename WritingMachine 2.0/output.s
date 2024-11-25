	.text
	.file	"<string>"
	.globl	Main
	.p2align	4, 0x90
Main:
	.cfi_startproc
	movabsq	$x_position, %rax
	addl	$3, (%rax)
	mfence
	movabsq	$pen_down, %rcx
	movb	$1, (%rcx)
	mfence
	addl	$2, (%rax)
	mfence
	movb	$0, (%rcx)
	mfence
	addl	$3, (%rax)
	mfence
	movb	$1, (%rcx)
	mfence
	movb	$0, (%rcx)
	mfence
	addl	$5, (%rax)
	mfence
	movb	$1, (%rcx)
	mfence
	addl	$2, (%rax)
	mfence
	retq
.Lfunc_end0:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
