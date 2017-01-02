
others=*.less

all: out/manual.css out/manual_prince.css out/mcdp_language_highlight.css out/manual_screen.css out/markdown.css

out/%.css: %.less $(others)
	lessc --verbose $< $@.tmp
	@cat banner.txt > $@
	@cat $@.tmp >> $@
	@rm $@.tmp
	@cat banner.txt >> $@
	-stylelint $@
