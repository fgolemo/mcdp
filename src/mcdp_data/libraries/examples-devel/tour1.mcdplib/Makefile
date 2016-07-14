markdowns=$(shell python get_list.py < tour1-toc.md)

tmpdir=.downloads
pdfs=$(markdowns:%.md=$(tmpdir)/%.pdf)

all: 
	echo "try: make manual"


tour.pdf: $(pdfs)
	pdftk  $^ output $@

$(tmpdir)/%.pdf: #: %.md
	mkdir -p $(tmpdir)
	rm -f $@
	wkhtmltopdf --print-media-type http://127.0.0.1:8080/libraries/tour1/$*.html\?print=1\&strict=1 $@.tmp.pdf
	mv $@.tmp.pdf $@
	

htmltmpdir=out-html
htmls=$(markdowns:%.md=$(htmltmpdir)/%.html)

$(htmltmpdir)/%.html:
	mkdir -p $(htmltmpdir)
	cd $(htmltmpdir) && wget -k -p -nd -nc http://127.0.0.1:8080/libraries/tour1/$*.html\?print=1\&strict=1
	mv $(htmltmpdir)/$*.html\?print=1\&strict=1 $(htmltmpdir)/$*.html

manual_html=$(htmltmpdir)/manual.html
manual: $(manual_html)

$(manual_html): $(htmls)
	python ./join_manual.py $(htmls) > $@
	python ./embed_images.py $@
	
manual.pdf: 
	wkhtmltopdf --print-media-type $(manual_html) $@

manual2:
	python ./join_manual.py $(htmls) > $(manual_html)
	python ./embed_images.py $(manual_html)

clean:
	rm -f $(pdfs)
	rm -f $(htmls)
	#rmdir $(tmpdir)

publish: $(htmltmpdir)/manual.html
	cp $< ~/env_mcdp/src/mcdp-gh-pages/media/pymcdp-manual.html
	cp $< ../../../../mcdp_web/static/manual.html



