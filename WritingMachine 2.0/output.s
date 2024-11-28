	.text
	.file	"<string>"
	.globl	Main
	.p2align	4, 0x90
Main:
	.cfi_startproc
	movabsq	$y_position, %rax
	movl	$4, (%rax)
	mfence
	movabsq	$pen_down, %rax
	movb	$1, (%rax)
	mfence
	retq
.Lfunc_end0:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
