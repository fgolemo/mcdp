
IMAGES := \
	$(wildcard src/*.expand_sides_white.png) \
	$(wildcard src/*.expand_sides_white.jpg) \
	$(wildcard src/*.expand_middle.jpg) \
	$(wildcard src/*.expand_sides_black.jpg) \
	$(wildcard src/*.crop_sides.jpg)         \
	$(wildcard src/*.crop_bottom.jpg)        \
	$(wildcard src/*.crop_top.jpg)           \
	$(wildcard src/*.crop_middle.jpg)        \
	$(wildcard src/*.crop_left.jpg)          \
	$(wildcard src/*.crop_right.jpg) 

TARGETS = \
	$(IMAGES:src/%.expand_sides_white.png=%.png)  \
	$(IMAGES:src/%.expand_sides_black.jpg=%.jpg)  \
	$(IMAGES:src/%.expand_sides_white.jpg=%.jpg)  \
	$(IMAGES:src/%.crop_sides.jpg=%.jpg)          \
	$(IMAGES:src/%.crop_bottom.jpg=%.jpg)         \
	$(IMAGES:src/%.crop_top.jpg=%.jpg)            \
	$(IMAGES:src/%.crop_middle.jpg=%.jpg)         \
	$(IMAGES:src/%.crop_left.jpg=%.jpg)           \
	$(IMAGES:src/%.crop_right.jpg=%.jpg) 


all: $(TARGETS)

clean:
	#
	# rm -f $(TARGETS)

height=1000
width=1514
size="$(width)x$(height)"

%.png:: src/%.expand_sides_white.png
	convert $< -resize $(size)    -background white -gravity center -extent $(size) $@

%.jpg:: src/%.expand_sides_white.jpg
	convert $< -resize $(size)    -background white -gravity center -extent $(size) $@

%.jpg:: src/%.expand_sides_black.jpg
	convert $< -resize $(size)    -background black -gravity center -extent $(size) $@

%.jpg:: src/%.crop_sides.jpg
	convert $< -resize x$(height) -background white -gravity center -extent $(size) $@

%.jpg:: src/%.crop_left.jpg
	convert $< -resize x$(height) -background white -gravity East -extent $(size) $@


%.jpg:: src/%.crop_bottom.jpg
	convert $< -resize $(width)x -background white -gravity North -extent $(size) $@

%.jpg:: src/%.crop_top.jpg
	convert $< -resize $(width)x -background white -gravity South -extent $(size) $@

%.jpg:: src/%.crop_middle.jpg
	convert $< -resize $(width)x -background white -gravity center -extent $(size) $@

%.jpg:: src/%.crop_right.jpg
	convert $< -resize x$(height) -background white -gravity West -extent $(size) $@
