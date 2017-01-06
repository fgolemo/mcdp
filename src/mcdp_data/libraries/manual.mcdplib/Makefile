

install:
	npm install MathJax-node jsdom less


# htmltmpdir=out-html

out=out-versions
out_intermediate=$(out)/intermediate
mcdp_render_manual_dir=$(out)/out-mcdp_render_manual
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


all:: $(all_targets)



# include commons/make/latex.mk
include commons/make/lyx.mk

%.md: %.tex
	./latex2md.py < $< > $@

%.pdf: %.md
	mcdp-render --pdf $* 

lyxes=$(wildcard docs/**/*.lyx)
generated_mds=$(lyxes:.lyx=.md)


#$(manual_pdf_wk)

# prince: $(manual_pdf_prince)
html: $(manual_html)


# .PHONY: $(manual_pdf_prince)
#
# $(manual_html): $(manual_tmp_html)
# 	# node prerender.js $^ $@
# 	cp $^ $@

# always check
# .PHONY: $(manual_html)

$(manual_html): $(generated_mds) $(wildcard docs/**/*)
	DISABLE_CONTRACTS=1 mcdp-render-manual \
		-o $(mcdp_render_manual_dir) \
		--output_file $@ -c "config echo 1; rparmake"
	#$(MAKE) extract-assets-manual

remake-join:
	compmake $(mcdp_render_manual_dir)/compmake -c 'config echo 1; clean *join*; parmake';

# extract-assets-manual:
# 	./extract-assets $(manual_html) $(manual_html)

# prerender:


# $(manual_pdf_wk):# $(manual_html)
# 	wkhtmltopdf --print-media-type $< $@

clean::
	rm -f $(generated_mds)
	rm -f $(targets)

realclean: clean
	# rm -rf $(mcdp_render_manual_dir)
	# rm -rf $(out)
	

publish: $(manual_html)
	# TODO: embed css
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	#cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	#cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html

.PHONY: css

css:
	@echo cssdir=$(cssdir)
	$(MAKE) -C $(cssdir)

$(out)/%.html: $(manual_html)
	sed 's@VERSIONCSS@$(cssprefix)/$*.css@' < $< > $@


$(out)/%.pdf: $(out)/%.html $(pdf_metadata) $(cssdir)/*less $(cssdir)/*css
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


