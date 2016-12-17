
htmltmpdir=out-html


manual_html=$(htmltmpdir)/manual.html
manual_pdf_wk=$(htmltmpdir)/manual-wk.pdf
manual_pdf_prince=$(htmltmpdir)/manual-prince.pdf

all: \
	$(manual_html) \
	$(manual_pdf_wk) \
	$(manual_pdf_prince)

prince: $(manual_pdf_prince)

.PHONY: $(manual_pdf_prince)

$(manual_html): 
	DISABLE_CONTRACTS=1 mcdp-render-manual --output_file $@ -c rparmake

$(manual_pdf_wk): $(manual_html)  
	wkhtmltopdf --print-media-type $< $@ 

clean:
	rm -rf out-mcdp-render-manual
	rm -rf $(manual_html)

publish: $(manual_html)
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html

prince_css=prince.css
$(manual_pdf_prince): $(manual_html) $(prince_css)
	prince -s $(prince_css) $< -o $@