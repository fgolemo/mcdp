#####
##
# Q: I try "make <file>.tex" and nothing happens!
# A: Maybe dependencies are off (files deleted and things like that)
#    Try to delete all: "rm *.lyx.d" and restart

#lyx?=/Applications/LyX.app/Contents/MacOS/lyx
lyx?=lyx

lyx_subdirs?=
lyx_files?=
lyx_generated_tex:=$(subst .lyx,.tex, $(lyx_files) )
lyx_generated_pdf:=$(subst .lyx,.pdf, $(lyx_files) )
# lyx_deps:=$(addprefix $(DEPDIR)/,$(subst .lyx,.lyx.d, $(lyx_files)))
lyx_deps:=$(subst .lyx,.lyx.d, $(lyx_files))
# we can create .tex indirectly
lyx_generated_tex_indirect:=$(subst .lyx,.tex, $(wildcard *.lyx) )
lyx_base=$(subst .lyx,, $(lyx_files))

lyx_debug:
	echo lyx_generated_pdf: $(lyx_generated_pdf)

# actually include all .lyx in the directory, not just the ones specified
# by lyx_files
all_lyx_base=$(subst .lyx,, $(wildcard *.lyx))

# FIXME
tmp_exts?=
lyx_tmp_files:=$(foreach base, $(all_lyx_base), $(foreach ext,$(tmp_exts), $(base)$(ext)))

all:: lyxmake lyxhide
clean:: lyxclean


lyxmake: $(lyx_generated_pdf)
	@#echo Making $(lyx_generated_pdf)

lyxtex: $(lyx_generated_tex)


%.lyx.d: %.lyx
	@echo "Creating dependencies file $@"
	@lyx-deps-all $< > $@

# if not given hypehn it shows alarming message
# http://www.makelinux.net/make3/make3-CHP-2-SECT-7
# 
# Jul 14: Disabling dependencies
# include $(lyx_deps)

# But if you do there might be other problems
# -include $(lyx_deps)

# Note we delete the .tex. otherwise lyx does not update the time
# and make always remake the file.

texflavor?=pdflatex

%.tex: %.lyx
	@-rm -f $@
	$(lyx) -e $(texflavor) -f all $<

# We redo the lyx, otherwise we would never be sure 
# whether this was compiled to a standalone or child document.
# TODO: detect if we need bibtex
# %.pdf: %.lyx
# 	$(lyx) -e pdflatex -f all $<
# 	pdflatex $(latex_args) $*
# 	- bibtex $*
# 	pdflatex $(latex_args) $* 
# 	pdflatex $(latex_args) $*
# 	# do not delete aux,blg,bbl for cross-references
# 	# Hide temporary files
# 	$(MAKE) texhide



lyxclean-%: 
	@$(MAKE) -C $* lyxclean

texclean::
	@-rm -f $(lyx_tmp_files)

lyxclean:: $(foreach s, $(lyx_subdirs), lyxclean-$s)
	@echo Cleaning LyX temporary files in $(CURDIR)
	@-rm -f $(lyx_generated_tex)
	@-rm -f $(lyx_generated_tex_indirect)
	@-rm -f $(lyx_generated_pdf)
	@-rm -f $(lyx_deps)
	@-rm -f $(lyx_tmp_files)
	@-rm -f \#*.lyx\#

%_conf.tex: %.lyx
	$(lyx) -x "branch-activate conf" -x "branch-deactivate report" -e pdflatex -f all $<
	mv $*.tex $@

%_report.tex: %.lyx
	$(lyx) -x "branch-deactivate conf" -x "branch-activate report" -e pdflatex -f all $<
	mv $*.tex $@

.SECONDARY:

	
lyxhide:
	@-chflags hidden $(lyx_generated_tex_indirect) 1>/dev/null 2>/dev/null || true
	@-chflags hidden $(lyx_generated_tex_indirect) 1>/dev/null 2>/dev/null || true
	@-chflags hidden $(lyx_tmp_files)     1>/dev/null 2>/dev/null || true
