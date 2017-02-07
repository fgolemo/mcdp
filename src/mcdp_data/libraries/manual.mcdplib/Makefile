all::

# htmltmpdir=out-html

out=out-versions
out_intermediate=$(out)/intermediate
mcdp_render_manual_dir=$(out)/out-mcdp_render_manual
mcdp_render_ready_dir=$(out)//out-mcdp_render_manual-ready
manual_html=$(out_intermediate)/manual.html

# vstring='1.0'

versions_html=v_manual_screen
versions_pdf=v_manual_blurb v_manual_ipad

# tmpfile=$(htmltmpdir)/.tmp.pdf

targets_html=$(foreach v, $(versions_html), $(out)/$(v).html)
targets_pdf=$(foreach v, $(versions_pdf),  $(out)/$(v).pdf )

all_targets=$(targets_html) $(targets_pdf)

pdf_metadata=pdf_metadata.txt

cssdir=$(realpath ../../../mcdp_web/static/css)
cssprefix=$(cssdir)/compiled


all:: \
	out-ready/ready-v_manual_blurb.pdf\
	out-ready/ready-v_manual_blurb_ready.pdf

all:: $(all_targets)



# include commons/make/latex.mk
include lyx.mk

# Latex conversion
%.md: %.tex
	./latex2md.py < $< > $@

%.pdf: %.md
	mcdp-render --pdf --stylesheet v_manual_blurb $*

%.html: %.md
	mcdp-render       --stylesheet v_manual_blurb $*

lyxes=$(wildcard docs/**/*.lyx)
generated_mds=$(lyxes:.lyx=.md)


# dot conversion
dots=$(wildcard docs/**/*.dot)
generated_graphs=$(dots:.dot=.svg)
#$(dots:.dot=.pdf)

# %.pdf: %.dot
# 	dot -Tpdf -o$@ $<
# 	@echo "Created $@"
%.svg: %.dot
	dot -Tsvg -o$@ $<
	@echo "Created $@"

generated=\
	$(generated_mds)\
	$(generated_graphs)

generated_files: $(generated)
	@echo $(generated)



html: $(manual_html)


$(manual_html): $(generated) $(wildcard docs/**/*)
	DISABLE_CONTRACTS=1 mcdp-render-manual \
		--src docs/ \
		-o $(mcdp_render_manual_dir) \
		--output_file $@ -c "config echo 1; rparmake"

ready_html=out-ready/ready.html
ready_src=manual-ready

$(ready_html): $(generated) $(wildcard $(ready_src)/**/*)
	DISABLE_CONTRACTS=1 mcdp-render-manual \
		--src $(ready_src) \
		-o $(mcdp_render_ready_dir) \
		--output_file $@ -c "config echo 1; rparmake"
	#$(MAKE) extract-assets-manual

remake-join:
	compmake $(mcdp_render_manual_dir)/compmake -c 'config echo 1; clean *join*; parmake';

# extract-assets-manual:
# 	./extract-assets $(manual_html) $(manual_html)

clean::
	rm -f $(generated)
	rm -f $(all_targets)

realclean: clean
	rm -rf $(out)
# rm -rf $(mcdp_render_manual_dir)


publish: $(manual_html)
	# TODO: embed css
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	#cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	#cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html

.PHONY: css

css:
	@echo cssdir=$(cssdir)
	$(MAKE) -C $(cssdir) -j

$(out)/%.html: $(manual_html)
	sed 's@VERSIONCSS@$(cssprefix)/$*.css@' < $< > $@

%-v_manual_blurb.html: %.html
	sed 's@VERSIONCSS@$(cssprefix)/v_manual_blurb.css@' < $< > $@
%-v_manual_blurb_ready.html: %.html
	sed 's@VERSIONCSS@$(cssprefix)/v_manual_blurb_ready.css@' < $< > $@



%.pdf: %.html $(pdf_metadata) $(cssdir)/*less $(cssdir)/*css
	$(MAKE) css
	prince --javascript $< -o $@.tmp
	pdftk $@.tmp update_info $(pdf_metadata) output $@
	pdftk $@ dump_data output $@.metadata.txt
	@rm -f $@.tmp
	pdftk $@ dump_data | grep PageMediaDimensions | head -n 1
	@echo "Expected size:"
	@echo "   441 x 666 points for Blurb/hardcover"
	@echo ""
	@echo "Written on:    $@"

prince-only:
	$(MAKE) css
	prince --javascript $(out)/v_manual_blurb.html -o $(out)/v_manual_blurb.pdf

	pdftk $(out)/v_manual_blurb.pdf dump_data | grep PageMediaDimensions | head -n 1
	@echo "Expected size:"
	@echo "   441 x 666 points for Blurb/hardcover"
	@echo ""
	@echo "Written on:    $@"

#
# lulu-6by9.pdf: $(manual_pdf_prince)
# 	echo User Preview to print to the page size -- pdfjam does not work
# 	# actually doesn't workopen
# 	# pdfjam --outfile  $@  --fitpaper true --papersize '{6.125in,9.250in}' $^
# 	# echo written $@


bibfile=all_only_one.bib
bibout=bibliography
bib: $(bibout)
$(bibout):
	bibtex2html -unicode --dl -o $(bibout) $(bibfile)




install:
	npm install MathJax-node jsdom less


# $(manual_pdf_wk):# $(manual_html)
# 	wkhtmltopdf --print-media-type $< $@
