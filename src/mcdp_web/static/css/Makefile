
others=colors.less

all: manual.css mcdp_language_highlight.css

%.css: %.less $(others)
	lessc --verbose $< $@.tmp
	@cat banner.txt > $@
	@cat $@.tmp >> $@
	@rm $@.tmp
	@cat banner.txt >> $@
	-stylelint $@
