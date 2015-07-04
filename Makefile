.PHONY: all app dependencies
.SUFFIXES:

all: app dependencies

app:
	+$(MAKE) -C app

dependencies:
	pip install -r requirements.txt
	+$(MAKE) -C app dependencies
