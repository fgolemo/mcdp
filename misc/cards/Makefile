cards="."

root=/Volumes/1506-boot-docs/boot-docs/ext/minimality_game
prepare="${root}/scripts/prepare.py"

out="../cards.out"

deck:
	$(MAKE) -C images
	python $(prepare) $(cards) $(out)
	$(MAKE) -C $(out)/cards -B -j5 deck.pdf
	ln -fs  $(out)/cards/deck.pdf
