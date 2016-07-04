markdowns=$(shell python get_list.py < toc.md)

tmpdir=.downloads
pdfs=$(markdowns:%.md=$(tmpdir)/%.pdf)

all: tour.pdf

tour.pdf: $(pdfs)
	pdftk  $^ output $@

$(tmpdir)/%.pdf: %.md
	mkdir -p $(tmpdir)
	wkhtmltopdf --print-media-type  http://127.0.0.1:8080/libraries/tour1/$*.html\?print=1 $@

clean:
	rm -f $(pdfs)
	rmdir $(tmpdir)

