all: build #publish


install:
	sudo apt-get install jekyll ruby-dev ruby-bundler
install-osx:
	bundle install --path vendor/bundle

serve:
	bundle exec jekyll serve
	
build:
	jekyll build

publish:
	surge _site/

