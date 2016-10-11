all: build publish


install:
	bundle install --path vendor/bundle

serve:
	bundle exec jekyll serve
	
build:
	jekyll build

publish:
	surge _site/

