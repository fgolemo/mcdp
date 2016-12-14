
all: manual


htmltmpdir=out-html


manual_html=$(htmltmpdir)/manual.html

manual: $(manual_html)

$(manual_html): 
	DISABLE_CONTRACTS=1 mcdp-render-manual --output_file $@ -c rparmake

manual.pdf: $(manual_html)  
	wkhtmltopdf --print-media-type $(manual_html) $@ 

clean:
	rm -rf out-mcdp-render-manual
	rm -rf $(manual_html)

publish: $(manual_html)
	#cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	cp $< ~/env_mcdp/src/mcdp/src/mcdp_web/static/manual.html
	cp $< ~/env_mcdp/src/mcdp/docs/media/pymcdp-manual.html