
others=*.less

d=compiled

# $(d)/manual.css \
# $(d)/manual_prince.css \
# $(d)/mcdp_language_highlight.css \
# $(d)/manual_screen.css \
# $(d)/markdown.css \

versions=$(wildcard v_*.less)
targets0=$(versions:.less=.css)
targets=$(foreach a, $(targets0), $(d)/$(a))


# targets=\
# 	$(d)/v_manual_ipad.css \
# 	$(d)/v_manual_blurb.css \
# 	$(d)/v_manual_screen.css \
# 	$(d)/v_standalone_ipad.css \
# 	$(d)/v_standalone_blurb.css \
# 	$(d)/v_standalone_screen.css \
# 	$(d)/v_mcdpweb.css

all: $(targets)


compiled/%.css: %.less $(others)
	lessc --verbose $< $@.tmp
	@cat banner.txt > $@
	@cat $@.tmp >> $@
	@rm $@.tmp
	@cat banner.txt >> $@
	-stylelint $@
