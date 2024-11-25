	.text
	.file	"<string>"
	.globl	linea2
	.p2align	4, 0x90
linea2:
	.cfi_startproc
	retq
.Lfunc_end0:
	.cfi_endproc

	.globl	linea1
	.p2align	4, 0x90
linea1:
	.cfi_startproc
	retq
.Lfunc_end1:
	.cfi_endproc

	.globl	Main
	.p2align	4, 0x90
Main:
	.cfi_startproc
	pushq	%rax
	.cfi_def_cfa_offset 16
	mfence
	movabsq	$pen_down, %rax
	movb	$1, (%rax)
	mfence
	movl	$1, 4(%rsp)
	movabsq	$x_position, %rax
	movabsq	$y_position, %rcx
	cmpl	$6, 4(%rsp)
	jg	.LBB2_3
	.p2align	4, 0x90
.LBB2_2:
	incl	4(%rsp)
	addl	$3, (%rax)
	mfence
	incl	(%rcx)
	mfence
	cmpl	$6, 4(%rsp)
	jle	.LBB2_2
.LBB2_3:
	popq	%rax
	retq
.Lfunc_end2:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
