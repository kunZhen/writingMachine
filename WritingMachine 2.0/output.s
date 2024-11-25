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
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$16, %rsp
	movl	$5, %eax
	movabsq	$x_position, %rcx
	.p2align	4, 0x90
.LBB2_1:
	movl	%eax, -4(%rbp)
	cmpl	$19, %eax
	jg	.LBB2_3
	addl	$90, (%rcx)
	movl	-4(%rbp), %eax
	incl	%eax
	jmp	.LBB2_1
.LBB2_3:
	movl	$16, %eax
	movabsq	$__chkstk, %r11
	callq	*%r11
	subq	%rax, %rsp
	movq	%rsp, %rax
	movl	$18, (%rax)
	movabsq	$y_position, %r8
	movl	$18, (%r8)
	movl	$1, %edx
	cmpl	$4, %edx
	jg	.LBB2_6
	.p2align	4, 0x90
.LBB2_5:
	incl	(%rax)
	movl	$19, (%r8)
	addl	$9, (%rcx)
	incl	%edx
	cmpl	$4, %edx
	jle	.LBB2_5
.LBB2_6:
	movq	%rbp, %rsp
	popq	%rbp
	retq
.Lfunc_end2:
	.cfi_endproc

	.comm	x_position,4,4
	.comm	y_position,4,4
	.comm	pen_down,1,1
