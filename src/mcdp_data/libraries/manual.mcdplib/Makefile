
htmltmpdir=out-html


manual_html=$(htmltmpdir)/manual.html
manual_tmp_html=$(htmltmpdir)/manual_tmp.html
manual_pdf_wk=$(htmltmpdir)/manual-wk.pdf
manual_pdf_prince=$(htmltmpdir)/manual-prince.pdf

all: \
	$(manual_html) \
	$(manual_pdf_prince)

#$(manual_pdf_wk)

install:
	npm install MathJax-node jsdom less

prince: $(manual_pdf_prince)
html: $(manual_html)


# .PHONY: $(manual_pdf_prince)
#
# $(manual_html): $(manual_tmp_html)
# 	# node prerender.js $^ $@
# 	cp $^ $@

# always check
.PHONY: $(manual_html)

$(manual_html): 
	DISABLE_CONTRACTS=1 mcdp-render-manual --output_file $@ -c "config echo 1; rparmake"
	$(MAKE) extract-assets-manual

extract-assets-manual:
	./extract-assets $(manual_html) $(manual_html)

# prerender:


$(manual_pdf_wk):# $(manual_html)
	wkhtmltopdf --print-media-type $< $@

clean:
	rm -rf out-mcdp-render-manual


realclean: clean
	rm -rf $(htmltmpdir)
	# rm -f $(manual_html)
	# rm -f $(manual_pdf_prince)

publish: $(manual_html)
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html

pdf_metadata=pdf_metadata.txt

cssdir=../../../mcdp_web/static/css

.PHONY: css

css:
	$(MAKE) -C $(cssdir)

tmpfile=$(htmltmpdir)/.tmp.pdf

$(manual_pdf_prince): $(manual_html) $(pdf_metadata) $(cssdir)/*less $(cssdir)/*css
	$(MAKE) css
	prince --javascript $< -o $(tmpfile)
	pdftk $(tmpfile) update_info $(pdf_metadata) output $@
	pdftk $@ dump_data output $@.metadata.txt
	@rm -f $(tmpfile)
	@echo ""
	@echo "Written on:    $@"

prince-only:
	$(MAKE) css
	prince --javascript $(manual_html) -o $(manual_pdf_prince)
	@echo ""
	@echo "Written on:    $(manual_pdf_prince)"

#
# lulu-6by9.pdf: $(manual_pdf_prince)
# 	echo User Preview to print to the page size -- pdfjam does not work
# 	# actually doesn't workopen
# 	# pdfjam --outfile  $@  --fitpaper true --papersize '{6.125in,9.250in}' $^
# 	# echo written $@

# lulu: lulu-6by9.pdf

bibfile=all_only_one.bib
bibout=bibliography
bib: $(bibout)
$(bibout):
	bibtex2html -unicode --dl -o $(bibout) $(bibfile)
