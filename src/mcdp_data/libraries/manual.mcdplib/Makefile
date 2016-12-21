
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
	npm install MathJax-node jsdom
	
prince: $(manual_pdf_prince)

.PHONY: $(manual_pdf_prince)

$(manual_html): $(manual_tmp_html)
	# node prerender.js $^ $@
	cp $^ $@

$(manual_tmp_html):
	DISABLE_CONTRACTS=1 mcdp-render-manual --output_file $@ -c "config echo 1; rparmake"
	
# prerender:


$(manual_pdf_wk): $(manual_html)  
	wkhtmltopdf --print-media-type $< $@ 

clean:
	rm -rf out-mcdp-render-manual
	rm -rf $(manual_html)
	rm -rf $(manual_tmp_html)

publish: $(manual_html)
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html


$(manual_pdf_prince): $(manual_html) 
	prince --javascript  $< -o $@


lulu-6by9.pdf: $(manual_pdf_prince)
	pdfjam --outfile  $@  --fitpaper true --papersize '{6.125in,9.250in}' $^
	echo written $<

lulu: lulu-6by9.pdf