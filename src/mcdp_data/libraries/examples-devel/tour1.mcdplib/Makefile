
markdowns=\
	tour_intro.md\
	tour_composition.md\
	tour_catalogue.md\
	tour_coproduct.md\
	tour_solution.md\
	tour_approximations.md\
	tour_uncertainty.md\
	tour_templates.md\
	space_rovers.md

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

